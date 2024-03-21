import pandas as pd
import plotly.express as px
from collections import Counter
import requests
import polars as pl

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

def summarize_jetbrains_data(proglang_data):
    if not isinstance(proglang_data, pl.DataFrame):
        raise TypeError("proglang_data must be a Polars DataFrame")
    # Updated to use `group_by` and `pl.len()` according to deprecation warnings and removed sorting
    language_counts = proglang_data.group_by('Language').agg(pl.len().alias('Count'))
    return language_counts

def main():
    statista_survey_df = load_statista_data()
    languages_df = load_stack_overflow_data()
    proglang_data_pl = load_jetbrains_data_polars()

    st.title('Programming Languages Surveys Visualization')

    survey_selection = st.sidebar.radio(
        "Choose a survey to display:",
        ('Stack Overflow Developer Survey', 'Statista Programming Survey', 'JetBrains Developer Ecosystem Survey 2022')
    )

    if survey_selection == 'Stack Overflow Developer Survey':
        st.header('Stack Overflow Developer Survey - Languages Worked With')
        fig_so = px.bar(languages_df, y='Language', x='Count', title='Top 10 Programming Languages Used According to Stack Overflow Survey', orientation='h')
        fig_so.update_layout(yaxis={'categoryorder': 'total descending'}, yaxis_title='Programming Language', xaxis_title='Count')
        st.plotly_chart(fig_so, use_container_width=True)

    elif survey_selection == 'Statista Programming Survey':
        st.header('Statista Programming Survey 2023')
        st.markdown("""
            This section presents data from the Statista survey on the most used programming languages worldwide among developers. 
            The data represents a snapshot of the programming landscape, showing the popularity of languages among 87,585 respondents. 
            For more details, [visit the Statista page](https://www.statista.com/statistics/793628/worldwide-developer-survey-most-used-languages/).
        """)
        # Removed the table display code for Statista survey as requested
        fig_statista = px.bar(statista_survey_df, x='Respondents', y='Language', text='Percentage', orientation='h', title='Top 10 Programming Languages by Number of Respondents')
        fig_statista.update_traces(texttemplate='%{text}%', textposition='inside')
        fig_statista.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Number of Respondents', yaxis_title=None)
        st.plotly_chart(fig_statista, use_container_width=True)

    elif survey_selection == 'JetBrains Developer Ecosystem Survey 2022':
        st.header('JetBrains Developer Ecosystem Survey 2022 - Top 10 Programming Languages')
        top_languages = summarize_jetbrains_data(proglang_data_pl)  # Summarize to get top languages

        # Create and display a bar plot directly from Polars DataFrame
        fig_jetbrains = px.bar(top_languages, x='Count', y='Language', orientation='h', title='Top 10 Programming Languages in JetBrains Developer Ecosystem Survey 2022')
        fig_jetbrains.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Count', yaxis_title='Programming Language')
        st.plotly_chart(fig_jetbrains, use_container_width=True)

if __name__ == "__main__":
    main()