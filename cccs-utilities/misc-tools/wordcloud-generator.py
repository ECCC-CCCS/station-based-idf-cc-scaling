"""
This utility loads a csv file into a Pandas dataframe, reads a column from this file,
and adds all words from this file into a wordcloud.

Notes:
    -Not sure if this works with multiword items.
"""

import pandas as pd
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

def make_wordcloud():
    fname="AB_ART_word_cloud.csv"
    column_name="words"

    df=pd.read_csv(fname)
    df[[column_name]].head()
    text=''
    for val in df.words:
        val=str(val)
        text += val+' '

    word_cloud=WordCloud(background_color="white", 
        width=1000,
        height=500).generate(text)

    plt.imshow(word_cloud,
          interpolation='bilinear')
    plt.axis("off")
    plt.show()

word_cloud.to_file("wordcloud.png")

def main():
    #Dummy calls - can modify for real use if required
    print("Yup you're here.")

if __name__ == "__main__":
    main()
