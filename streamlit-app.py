import streamlit as st
import pandas as pd
import plotly.express as px
import polars as pl
from collections import Counter

def load_statista_data():
    statista_survey_df = pd.read_excel('data/statista-programming-survey-2023.xlsx', sheet_name='Data', usecols="B:C", skiprows=4, nrows=10)
    total_respondents = 87585
    statista_survey_df.columns = ['Language', 'Percentage']
    statista_survey_df['Percentage'] = round(statista_survey_df['Percentage']).astype(int)
    statista_survey_df['Respondents'] = round((statista_survey_df['Percentage'] / 100) * total_respondents).astype(int)
    return statista_survey_df

def load_stack_overflow_data():
    so_survey_df = pd.read_csv('data/stack-overflow-developer-survey-2023/survey_results_public.csv', usecols=['LanguageHaveWorkedWith'])
    language_counter = Counter()
    for row in so_survey_df['LanguageHaveWorkedWith'].dropna():
        languages = row.split(';')
        language_counter.update(languages)
    languages_df = pd.DataFrame(language_counter.items(), columns=['Language', 'Count']).sort_values(by='Count', ascending=False).head(10)
    return languages_df

def load_jetbrains_data_polars():
    jetbrains_df = pl.read_csv('data/jetbrains-developer-ecosystem-2022.csv', columns=['variable', 'value'])
    filtered_df = jetbrains_df.filter(pl.col('variable').str.contains('proglang'))
    proglang_data = filtered_df.select(pl.col('value').alias('Language'))
    return proglang_data

def main():
    statista_survey_df = load_statista_data()
    languages_df = load_stack_overflow_data()
    proglang_data = load_jetbrains_data_polars()

    st.title('Programming Languages Surveys Visualization')

    survey_selection = st.sidebar.radio(
        "Choose a survey to display:",
        ('Statista Programming Survey', 'Stack Overflow Developer Survey', 'JetBrains Developer Ecosystem Survey 2022')
    )

    if survey_selection == 'Statista Programming Survey':
        st.header('Statista Programming Survey 2023')
        # Statista survey section code...
        st.markdown("""
            This section presents data from the Statista survey on the most used programming languages worldwide among developers. 
            The data represents a snapshot of the programming landscape, showing the popularity of languages among 87,585 respondents. 
            For more details, [visit the Statista page](https://www.statista.com/statistics/793628/worldwide-developer-survey-most-used-languages/).
        """)
        fig_statista = px.bar(statista_survey_df, x='Respondents', y='Language', text='Percentage', orientation='h', title='Top 10 Programming Languages by Number of Respondents')
        fig_statista.update_traces(texttemplate='%{text}%', textposition='inside')
        fig_statista.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Number of Respondents', yaxis_title=None)
        st.plotly_chart(fig_statista, use_container_width=True)

    elif survey_selection == 'Stack Overflow Developer Survey':
        st.header('Stack Overflow Developer Survey - Languages Worked With')
        # Stack Overflow section code...
        st.markdown("""
            This section presents the top 10 programming languages that developers have worked with according to the Stack Overflow Developer Survey 2023. 
            To explore more about this survey and its findings, [visit the survey website](https://survey.stackoverflow.co/2023/).
        """)
        # Sort the data in descending order
        languages_df = languages_df.sort_values(by='Count', ascending=True)
        fig_so = px.bar(languages_df, y='Language', x='Count', title='Top 10 Programming Languages Used According to Stack Overflow Survey', orientation='h')
        fig_so.update_layout(yaxis={'categoryorder': 'total descending'}, yaxis_title='Programming Language', xaxis_title='Count')
        st.plotly_chart(fig_so, use_container_width=True)

    elif survey_selection == 'JetBrains Developer Ecosystem Survey 2022':
        st.header('JetBrains Developer Ecosystem Survey 2022 - Top Programming Languages')
        # JetBrains survey section code...
        st.markdown("""
            This section highlights the top programming languages as revealed by the JetBrains Developer Ecosystem Survey 2022. 
            For a deeper dive into the survey's insights, [check out their website](https://www.jetbrains.com/lp/devecosystem-2022/).
        """)
        # Load the data
        proglang_data = load_jetbrains_data_polars()

        # Count the occurrences of each programming language
        language_counts = proglang_data.group_by('Language').agg(pl.count('Language').alias('count'))

        # Convert to Pandas DataFrame
        language_counts_pandas = language_counts.to_pandas()

        # Sort in ascending order (for correct Plotly display) and select the top 10
        top_languages = language_counts_pandas.sort_values(by='count', ascending=True).tail(10)

        # Plotting using Plotly Express with dark mode for the top 10 languages
        plot_fig = px.bar(top_languages, y='Language', x='count',
                          title="Top 10 Programming Languages",
                          labels={'count': 'Count', 'Language': 'Programming Language'},
                          orientation='h')  # Horizontal bars
        plot_fig.update_layout(template='plotly_dark', xaxis_title='Count', yaxis_title='Programming Language')
        st.plotly_chart(plot_fig, use_container_width=True)

if __name__ == "__main__":
    main()
