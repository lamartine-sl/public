# View number of unique values per column 
def visualize_unique_values(df, columns):
    # Import matplotlib.pyplot and pandas
    import matplotlib.pyplot as plt
    import pandas as pd

    # Calculate number of unique values for each label: num_unique_labels
    num_unique_labels = df[columns].apply(pd.Series.nunique)

    # Plot number of unique values for each label
    num_unique_labels.plot(kind='bar')

    # Label the axes
    plt.xlabel('Labels')
    plt.ylabel('Number of unique values')

    # Display the plot
    plt.show()