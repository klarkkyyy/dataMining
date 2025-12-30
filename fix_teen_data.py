#!/usr/bin/env python3
"""
Script to expand teen age range from 18-19 to 13-19 and update platform preferences
and social media time based on realistic teen behavior patterns.

Reads and overwrites social_media_vs_productivity_CORRECTED.csv
"""

import pandas as pd
import numpy as np
from collections import Counter

# Set random seed for reproducibility
np.random.seed(42)

# Define age group platform probabilities
AGE_PLATFORM_PROBABILITIES = {
    'early_teen': {  # 13-14
        'platforms': ['TikTok', 'Instagram', 'Snapchat', 'Twitter', 'Facebook'],
        'probabilities': [0.65, 0.20, 0.10, 0.03, 0.02]
    },
    'high_school': {  # 15-17
        'platforms': ['Instagram', 'TikTok', 'Snapchat', 'Twitter', 'Facebook'],
        'probabilities': [0.45, 0.35, 0.12, 0.05, 0.03]
    },
    'college_freshman': {  # 18-19
        'platforms': ['Instagram', 'TikTok', 'Twitter', 'Snapchat', 'Facebook'],
        'probabilities': [0.40, 0.35, 0.15, 0.05, 0.05]
    }
}

# Define social media time ranges by age group and platform (hours per day)
SOCIAL_MEDIA_TIME_RANGES = {
    'early_teen': {  # 13-14
        'TikTok': (6.0, 9.0),
        'Instagram': (4.5, 7.0),
        'Snapchat': (3.5, 6.0),
        'Twitter': (2.0, 4.5),
        'Facebook': (2.0, 4.5)
    },
    'high_school': {  # 15-17
        'Instagram': (5.0, 8.0),
        'TikTok': (4.5, 7.5),
        'Snapchat': (3.0, 5.5),
        'Twitter': (1.5, 4.0),
        'Facebook': (1.5, 4.0)
    },
    'college_freshman': {  # 18-19
        'TikTok': (4.5, 8.0),
        'Instagram': (3.5, 6.5),
        'Twitter': (1.5, 4.0),
        'Snapchat': (1.5, 4.0),
        'Facebook': (1.5, 4.0)
    }
}


def get_teen_age_group(age):
    """
    Classify teen age into age groups.
    
    Args:
        age: Age as a float
        
    Returns:
        Age group key string or None
    """
    if pd.isna(age):
        return None
    
    age = float(age)
    
    if 13 <= age <= 14:
        return 'early_teen'
    elif 15 <= age <= 17:
        return 'high_school'
    elif 18 <= age <= 19:
        return 'college_freshman'
    else:
        return None


def assign_platform_by_teen_age(age):
    """
    Assign a social media platform based on teen age group probabilities.
    
    Args:
        age: Age as a float
        
    Returns:
        Platform name
    """
    age_group = get_teen_age_group(age)
    
    if age_group is None:
        return None
    
    platforms = AGE_PLATFORM_PROBABILITIES[age_group]['platforms']
    probabilities = AGE_PLATFORM_PROBABILITIES[age_group]['probabilities']
    
    selected_platform = np.random.choice(platforms, p=probabilities)
    
    return selected_platform


def assign_social_media_time(age, platform):
    """
    Assign realistic daily social media time based on age group and platform.
    
    Args:
        age: Age as a float
        platform: Social media platform name
        
    Returns:
        Daily social media time in hours
    """
    age_group = get_teen_age_group(age)
    
    if age_group is None or pd.isna(platform) or platform == '':
        return None
    
    # Get time range for this age group and platform
    time_ranges = SOCIAL_MEDIA_TIME_RANGES[age_group]
    
    if platform in time_ranges:
        min_time, max_time = time_ranges[platform]
    else:
        # Default for other platforms
        if age_group == 'early_teen':
            min_time, max_time = 2.0, 4.5
        elif age_group == 'high_school':
            min_time, max_time = 1.5, 4.0
        else:  # college_freshman
            min_time, max_time = 1.5, 4.0
    
    # Generate random time within range
    time = np.random.uniform(min_time, max_time)
    
    return time


def expand_teen_ages(df):
    """
    Expand teen age range from 18-19 to 13-19.
    
    Args:
        df: DataFrame with teen data
        
    Returns:
        Modified DataFrame with expanded age range
    """
    # Find all rows with age 18.0 or 19.0
    teen_mask = df['age'].isin([18.0, 19.0])
    teen_count = teen_mask.sum()
    
    print(f"Found {teen_count} teens with ages 18-19")
    
    # Randomly assign new ages from 13.0 to 19.0 (7 possible ages)
    new_ages = np.random.choice(
        [13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],
        size=teen_count,
        replace=True
    )
    
    # Update ages for teen rows
    df.loc[teen_mask, 'age'] = new_ages
    
    print(f"Redistributed ages across 13.0-19.0")
    
    return df


def update_teen_platforms_and_time(df):
    """
    Update platform preferences and social media time for teens (ages 13-19).
    
    Args:
        df: DataFrame with teen data
        
    Returns:
        Modified DataFrame with updated platforms and times
    """
    # Find all teen rows (ages 13-19)
    teen_mask = df['age'].isin([13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0])
    teen_indices = df[teen_mask].index
    
    print(f"Updating {len(teen_indices)} teen rows...")
    
    # Update platform preferences
    for idx in teen_indices:
        age = df.loc[idx, 'age']
        new_platform = assign_platform_by_teen_age(age)
        df.loc[idx, 'social_platform_preference'] = new_platform
    
    print(f"Updated platform preferences for all teens")
    
    # Update social media times
    for idx in teen_indices:
        age = df.loc[idx, 'age']
        platform = df.loc[idx, 'social_platform_preference']
        new_time = assign_social_media_time(age, platform)
        if new_time is not None:
            df.loc[idx, 'daily_social_media_time'] = new_time
    
    print(f"Updated daily social media times for all teens")
    
    return df


def verify_teen_distribution(df):
    """
    Verify the teen age distribution, platform preferences, and social media time.
    
    Args:
        df: DataFrame with corrected teen data
    """
    print("\n" + "="*80)
    print("VERIFICATION: Teen Age Distribution, Platforms, and Social Media Time")
    print("="*80)
    
    # Age distribution
    teen_df = df[df['age'].isin([13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0])]
    print(f"\nTotal teens (ages 13-19): {len(teen_df)}")
    print("\nAge Distribution:")
    age_counts = teen_df['age'].value_counts().sort_index()
    for age, count in age_counts.items():
        percentage = (count / len(teen_df)) * 100
        print(f"  Age {int(age):2d}: {count:4d} ({percentage:5.2f}%)")
    
    # Platform preferences by age group
    age_groups = [
        ([13.0, 14.0], 'Ages 13-14 (Early Teens)'),
        ([15.0, 16.0, 17.0], 'Ages 15-17 (High School)'),
        ([18.0, 19.0], 'Ages 18-19 (College Freshmen)')
    ]
    
    print("\n" + "-"*80)
    print("Platform Preferences by Age Group:")
    print("-"*80)
    
    for ages, label in age_groups:
        group_df = teen_df[teen_df['age'].isin(ages)]
        if len(group_df) > 0:
            print(f"\n{label} (n={len(group_df)}):")
            platform_counts = group_df['social_platform_preference'].value_counts()
            for platform, count in platform_counts.items():
                percentage = (count / len(group_df)) * 100
                print(f"  {platform:12s}: {count:4d} ({percentage:5.2f}%)")
    
    # Average social media time by age group and platform
    print("\n" + "-"*80)
    print("Average Daily Social Media Time by Age Group and Platform:")
    print("-"*80)
    
    for ages, label in age_groups:
        group_df = teen_df[teen_df['age'].isin(ages)]
        if len(group_df) > 0:
            print(f"\n{label}:")
            # Group by platform and calculate mean time
            platforms = group_df['social_platform_preference'].unique()
            for platform in sorted(platforms):
                platform_df = group_df[group_df['social_platform_preference'] == platform]
                avg_time = platform_df['daily_social_media_time'].mean()
                min_time = platform_df['daily_social_media_time'].min()
                max_time = platform_df['daily_social_media_time'].max()
                print(f"  {platform:12s}: avg={avg_time:5.2f} hrs/day (range: {min_time:.2f}-{max_time:.2f})")
    
    print("\n" + "="*80)


def main():
    """
    Main function to execute the teen data correction.
    """
    input_file = 'social_media_vs_productivity_CORRECTED.csv'
    output_file = 'social_media_vs_productivity_CORRECTED.csv'
    
    print("="*80)
    print("FIX TEEN DATA: Expand Age Range (13-19) and Update Preferences")
    print("="*80)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Read the dataset
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Total rows: {len(df)}")
    
    # Expand teen ages from 18-19 to 13-19
    print("\n" + "-"*80)
    print("Step 1: Expanding teen age range from 18-19 to 13-19")
    print("-"*80)
    df = expand_teen_ages(df)
    
    # Update platform preferences and social media time
    print("\n" + "-"*80)
    print("Step 2: Updating platform preferences and social media time")
    print("-"*80)
    df = update_teen_platforms_and_time(df)
    
    # Save the corrected dataset
    print("\n" + "-"*80)
    print(f"Saving to {output_file}...")
    df.to_csv(output_file, index=False)
    print(f"✅ Successfully saved corrected dataset to {output_file}")
    
    # Verify the results
    verify_teen_distribution(df)
    
    print("\n" + "="*80)
    print("✅ COMPLETE! Teen dataset now has realistic age range and behavior patterns.")
    print("="*80)


if __name__ == '__main__':
    main()
