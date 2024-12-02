import streamlit as st
import pandas as pd
import re

def clean_rule_name_for_sql(name):
    # Convert to snake case and clean special characters
    clean = name.lower()
    clean = clean.replace("'", "''")  # Escape single quotes for SQL
    clean = re.sub(r'[^a-zA-Z0-9\s_]', '', clean)  # Remove special chars except underscore
    clean = re.sub(r'\s+', '_', clean.strip())  # Replace spaces with underscore
    return clean

def generate_sql_case(rule_name):
    sql_col_name = clean_rule_name_for_sql(rule_name)
    escaped_rule_name = rule_name.replace("'", "''")
    return f"CASE WHEN es.raw_response::jsonb->'data'->>'applied_rules' ILIKE '%{escaped_rule_name}%' THEN 1 ELSE 0 END as {sql_col_name}"

def process_csv(df):
    # Extract name and score/action columns
    processed_df = df[['name', 'actionDetails']].copy()
    processed_df.columns = ['Rule Name', 'Score/Action']
    
    # Generate SQL cases
    sql_cases = []
    for rule_name in df['name']:
        sql_cases.append(generate_sql_case(rule_name))
    
    sql_output = ',\n'.join(sql_cases)
    
    return processed_df, sql_output

def main():
    st.title("Fraud Rules Processor")
    st.write("Upload a CSV file with fraud rules to process and generate SQL cases.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Read CSV with semicolon separator and handle quotes
        df = pd.read_csv(uploaded_file, sep=';', quotechar='"')
        
        # Process the data
        processed_df, sql_output = process_csv(df)
        
        # Display the simplified rules table
        st.header("Simplified Rules Table")
        st.dataframe(processed_df)
        
        # Display the SQL output
        st.header("SQL CASE Statements")
        st.text_area("SQL Output", sql_output, height=400)
        
        # Add download buttons
        st.download_button(
            label="Download Rules CSV",
            data=processed_df.to_csv(index=False).encode('utf-8'),
            file_name="processed_rules.csv",
            mime="text/csv"
        )
        
        st.download_button(
            label="Download SQL File",
            data=sql_output,
            file_name="rules_sql_cases.sql",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()