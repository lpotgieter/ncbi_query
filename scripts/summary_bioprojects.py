import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def load_sample_data(csv_file):
    df = pd.read_csv(csv_file)
    return df

# bar plot counting number of species
def plot_species_counts(df, prefix):
    species_counts = df['species'].value_counts()
    plt.figure()
    sns.countplot(data=df, x='species', order=df['species'].value_counts().index)
    plt.xlabel('Species')
    plt.ylabel('Count')
    plt.title('Species Frequency')
    plt.xticks(rotation=90)
    plt.tight_layout()
    filename = f"{prefix}_species_counts.png"
    plt.savefig(filename)
    print(f"Plot saved to {filename}")
    plt.show()

def summarise_to_csv(df, prefix):
    """
    Write a summary CSV with per-species counts of samples,
    unique geographic locations, and unique owners.
    """
    summary = (
        df.groupby('species')
        .agg(
            sample_count=('sample_id', 'count'),
            unique_locations=('geo_loc_name', 'nunique'),
            unique_owners=('owner_name', 'nunique')
        )
        .reset_index()
        .sort_values('sample_count', ascending=False)
    )

    filename = f"{prefix}_summary.csv"
    summary.to_csv(filename, index=False)
    print(f"Summary saved to {filename}")
    return summary

def parse_arguments():
    parser = argparse.ArgumentParser(description='Analyse BioSample data')
    parser.add_argument('--csv-file', required=True, help='CSV file from fetch_biosample.py')
    parser.add_argument('--prefix', default='out', help='Prefix for plots')
    return parser.parse_args()

def main():
    args = parse_arguments()
    try:
        df = load_sample_data(args.csv_file)
        plot_species_counts(df, args.prefix)
        summarise_to_csv(df, args.prefix)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()