import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from textblob import TextBlob
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext


class Article:
    def __init__(self, title, source, summary, sentiment):
        self.title = title
        self.source = source
        self.summary = summary
        self.sentiment = sentiment


class EnvironmentalNewsSummarizer:
    def __init__(self):
        self.articles = []
        self.sources = []
        self.model = pipeline("summarization")

    def scrape_news_websites(self):
        for source in self.sources:
            response = requests.get(source)
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("article")

            for article in articles:
                title = article.find("h2").text.strip()
                summary = article.find("p").text.strip()
                article_url = article.find("a")["href"]
                sentiment = self.analyze_sentiment(summary)

                self.articles.append(
                    Article(title, source, summary, sentiment))

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"

    def summarize_articles(self):
        for article in self.articles:
            summary = self.model(
                article.summary, max_length=100, min_length=30, do_sample=False)
            article.summary = summary[0]['summary_text']

    def filter_articles(self, topic):
        filtered_articles = []
        for article in self.articles:
            if topic.lower() in article.summary.lower():
                filtered_articles.append(article)

        return filtered_articles


class GUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Environmental News Summarizer")

        self.label_topic = tk.Label(window, text="Topic:")
        self.label_topic.pack()

        self.entry_topic = tk.Entry(window)
        self.entry_topic.pack()

        self.label_sources = tk.Label(window, text="News Sources:")
        self.label_sources.pack()

        self.checkbutton_sources = []
        self.news_sources = [
            "https://www.example.com/source1",
            "https://www.example.com/source2",
            "https://www.example.com/source3"
        ]

        for source in self.news_sources:
            var = tk.IntVar()
            checkbutton = tk.Checkbutton(window, text=source,
                                         variable=var,
                                         command=self.update_sources)
            checkbutton.pack()
            self.checkbutton_sources.append((checkbutton, source))

        self.label_summary = tk.Label(window, text="Summary:")
        self.label_summary.pack()

        self.text_summary = scrolledtext.ScrolledText(
            window, height=10, width=50)
        self.text_summary.pack()

        self.button_refresh = tk.Button(
            window, text="Refresh", command=self.refresh_articles)
        self.button_refresh.pack()

        self.button_filter = tk.Button(
            window, text="Filter", command=self.filter_articles)
        self.button_filter.pack()

        self.scraper = EnvironmentalNewsSummarizer()

    def refresh_articles(self):
        self.scraper.scrape_news_websites()
        self.scraper.summarize_articles()

    def filter_articles(self):
        topic = self.entry_topic.get().lower()
        if topic:
            filtered_articles = self.scraper.filter_articles(topic)
            if filtered_articles:
                self.display_summary(filtered_articles[0])
            else:
                messagebox.showinfo(
                    "No Articles Found", "No articles found related to the specified topic.")
        else:
            messagebox.showinfo("Topic Not Specified",
                                "Please enter a topic to filter the articles.")

    def update_sources(self):
        self.scraper.sources = [
            source for checkbutton, source in self.checkbutton_sources if checkbutton.get() == 1]

    def display_summary(self, article):
        self.text_summary.delete(1.0, tk.END)
        self.text_summary.insert(tk.END, f"Title: {article.title}\n")
        self.text_summary.insert(tk.END, f"Source: {article.source}\n")
        self.text_summary.insert(tk.END, f"Sentiment: {article.sentiment}\n")
        self.text_summary.insert(tk.END, "Summary:\n")
        self.text_summary.insert(tk.END, f"{article.summary}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    window = tk.Tk()
    gui = GUI(window)
    gui.run()
