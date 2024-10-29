import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def eda_section():
    st.header("Exploratory Data Analysis (EDA)")

    tabs = st.tabs(["Data Overview", "Missing Values", "Distribution Analysis", 
                    "Categorical Analysis", "Correlation Study", "Outlier Detection", 
                    "Pair Plot", "Feature Relationships"])

    with tabs[0]:
        data_overview()
    with tabs[1]:
        missing_values_analysis()
    with tabs[2]:
        distribution_analysis()
    with tabs[3]:
        categorical_analysis()
    with tabs[4]:
        correlation_study()
    with tabs[5]:
        outlier_detection()
    with tabs[6]:
        pair_plot()
    with tabs[7]:
        feature_relationships()

def data_overview():
    data = st.session_state['data']
    st.subheader("Data Overview")
    st.write("First few rows of the dataset:")
    st.dataframe(data.head())

    st.write("Basic statistical details:")
    st.write(data.describe(include='all'))

def missing_values_analysis():
    data = st.session_state['data']
    st.subheader("Missing Values Analysis")
    missing_values = data.isnull().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        st.write("Missing values per column:")
        st.write(missing_values)
    else:
        st.write("No missing values detected.")

    # Optional: Visualize missing values heatmap
    if st.checkbox("Show missing values heatmap"):
        import missingno as msno
        fig = plt.figure()
        msno.matrix(data, figsize=(10, 6))
        st.pyplot(fig)

def distribution_analysis():
    data = st.session_state['data']
    st.subheader("Distribution Analysis")
    numeric_cols = data.select_dtypes(include=['float', 'int']).columns.tolist()
    if numeric_cols:
        selected_cols = st.multiselect("Select numeric columns for distribution analysis", numeric_cols)
        plot_type = st.selectbox("Select plot type", ["Histogram", "Box Plot", "Violin Plot", "KDE Plot"])
        for col in selected_cols:
            st.write(f"{plot_type} of {col}")
            if plot_type == "Histogram":
                fig = px.histogram(data, x=col, title=f"Histogram of {col}")
                st.plotly_chart(fig)
            elif plot_type == "Box Plot":
                fig = px.box(data, y=col, title=f"Box Plot of {col}")
                st.plotly_chart(fig)
            elif plot_type == "Violin Plot":
                fig = px.violin(data, y=col, box=True, title=f"Violin Plot of {col}")
                st.plotly_chart(fig)
            elif plot_type == "KDE Plot":
                fig = plt.figure()
                sns.kdeplot(data[col], shade=True)
                plt.title(f"KDE Plot of {col}")
                st.pyplot(fig)
    else:
        st.write("No numeric columns available for distribution analysis.")

def categorical_analysis():
    data = st.session_state['data']
    st.subheader("Categorical Variable Analysis")
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    if categorical_cols:
        selected_cols = st.multiselect("Select categorical columns for analysis", categorical_cols)
        for col in selected_cols:
            st.write(f"Value counts for {col}:")
            st.write(data[col].value_counts())

            fig = px.bar(data[col].value_counts().reset_index(), x='index', y=col, 
                         labels={'index': col, col: 'Count'}, title=f"Bar plot of {col}")
            st.plotly_chart(fig)
    else:
        st.write("No categorical columns available for analysis.")

def correlation_study():
    data = st.session_state['data']
    st.subheader("Correlation Study")
    numeric_cols = data.select_dtypes(include=['float', 'int']).columns.tolist()
    if len(numeric_cols) > 1:
        selected_cols = st.multiselect("Select numeric columns for correlation", numeric_cols, default=numeric_cols)
        corr_method = st.selectbox("Select correlation method", ["Pearson", "Spearman", "Kendall"])
        
        # Compute the correlation matrix
        corr_matrix = data[selected_cols].corr(method=corr_method.lower())
        
        # Dynamically adjust figure size based on the number of variables
        fig_size = max(10, len(selected_cols) * 0.8)
        
        # Generate a heatmap with custom figure size, color map, and annotations for readability
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", square=True, 
                    cbar_kws={'shrink': 0.8}, linewidths=0.5, annot_kws={"size": 10})
        
        # Set the title and layout adjustments for readability
        plt.title(f"{corr_method} Correlation Matrix", fontsize=15)
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.yticks(rotation=0, fontsize=10)
        
        st.pyplot(fig)
    else:
        st.write("Not enough numeric columns to compute correlations.")

def outlier_detection():
    data = st.session_state['data']
    st.subheader("Outlier Detection")
    numeric_cols = data.select_dtypes(include=['float', 'int']).columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("Select a numeric column for outlier detection", numeric_cols)
        method = st.selectbox("Select outlier detection method", ["IQR Method", "Z-Score Method", "Isolation Forest"])
        
        if method == "IQR Method":
            fig = px.box(data, y=selected_col, title=f"Box Plot of {selected_col}")
            st.plotly_chart(fig)
            q1 = data[selected_col].quantile(0.25)
            q3 = data[selected_col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = data[(data[selected_col] < lower_bound) | (data[selected_col] > upper_bound)]
            st.write(f"Number of outliers in {selected_col} using IQR method: {len(outliers)}")
        
        elif method == "Z-Score Method":
            from scipy import stats
            data['z_score'] = stats.zscore(data[selected_col])
            outliers = data[(data['z_score'] > 3) | (data['z_score'] < -3)]
            st.write(f"Number of outliers in {selected_col} using Z-Score method: {len(outliers)}")
            fig = px.histogram(data, x='z_score', title=f"Z-Score Distribution for {selected_col}")
            st.plotly_chart(fig)
            data.drop(columns=['z_score'], inplace=True)
        
        elif method == "Isolation Forest":
            from sklearn.ensemble import IsolationForest
            model = IsolationForest(contamination=0.05)
            data['anomaly'] = model.fit_predict(data[[selected_col]])
            outliers = data[data['anomaly'] == -1]
            st.write(f"Number of outliers in {selected_col} using Isolation Forest: {len(outliers)}")
            fig = px.scatter(data, y=selected_col, color='anomaly', title=f"Isolation Forest Outlier Detection for {selected_col}")
            st.plotly_chart(fig)
            data.drop(columns=['anomaly'], inplace=True)
    else:
        st.write("No numeric columns available for outlier detection.")

def pair_plot():
    data = st.session_state['data']
    st.subheader("Pair Plot")
    numeric_cols = data.select_dtypes(include=['float', 'int']).columns.tolist()
    if len(numeric_cols) > 1:
        selected_cols = st.multiselect("Select numeric columns for pair plot", numeric_cols, default=numeric_cols)
        color_col = st.selectbox("Select a categorical column for color encoding (optional)", [None] + data.select_dtypes(include=['object', 'category']).columns.tolist())
        if st.button("Generate Pair Plot"):
            if color_col:
                fig = px.scatter_matrix(data, dimensions=selected_cols, color=color_col)
            else:
                fig = px.scatter_matrix(data, dimensions=selected_cols)
            st.plotly_chart(fig)
    else:
        st.write("Not enough numeric columns to generate a pair plot.")

def feature_relationships():
    data = st.session_state['data']
    st.subheader("Feature Relationships")
    numeric_cols = data.select_dtypes(include=['float', 'int']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select a numeric column", numeric_cols)
        cat_col = st.selectbox("Select a categorical column", categorical_cols)
        plot_type = st.selectbox("Select plot type", ["Box Plot", "Violin Plot", "Bar Plot"])
        if plot_type == "Box Plot":
            fig = px.box(data, x=cat_col, y=num_col, title=f"{num_col} vs {cat_col}")
            st.plotly_chart(fig)
        elif plot_type == "Violin Plot":
            fig = px.violin(data, x=cat_col, y=num_col, box=True, title=f"{num_col} vs {cat_col}")
            st.plotly_chart(fig)
        elif plot_type == "Bar Plot":
            aggregated_data = data.groupby(cat_col)[num_col].mean().reset_index()
            fig = px.bar(aggregated_data, x=cat_col, y=num_col, title=f"Average {num_col} by {cat_col}")
            st.plotly_chart(fig)
    else:
        st.write("Not enough numeric or categorical columns to analyze feature relationships.")