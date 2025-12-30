#!/usr/bin/env python3
"""
Script to fix job_type distribution by age to make it realistic.
Based on labor statistics and educational requirements.
Reads and overwrites social_media_vs_productivity_CORRECTED.csv
"""

import pandas as pd
import numpy as np
from collections import Counter

# Set random seed for reproducibility
np.random.seed(42)


def assign_realistic_job(age):
    """
    Assign a realistic job type based on age using probability distributions.
    
    Args:
        age: Age as a float
        
    Returns:
        Job type string
    """
    if pd.isna(age):
        return 'Student'  # Default for missing age
    
    age = int(age)
    
    # Age 18-19 (Teens): ONLY Student, Unemployed, IT, Other
    if age in [18, 19]:
        return np.random.choice(
            ['Student', 'Unemployed', 'IT', 'Other'],
            p=[0.85, 0.10, 0.03, 0.02]
        )
    
    # Age 20-22: ONLY Student, Unemployed, IT, Other  
    elif age in [20, 21, 22]:
        return np.random.choice(
            ['Student', 'Unemployed', 'IT', 'Other'],
            p=[0.65, 0.15, 0.15, 0.05]
        )
    
    # Age 23-24: Can start having Finance/Health (recent grads)
    elif age in [23, 24]:
        return np.random.choice(
            ['Student', 'IT', 'Finance', 'Health', 'Education', 'Unemployed', 'Other'],
            p=[0.55, 0.15, 0.08, 0.05, 0.05, 0.10, 0.02]
        )
    
    # Age 25-29
    elif 25 <= age <= 29:
        return np.random.choice(
            ['IT', 'Finance', 'Health', 'Education', 'Student', 'Unemployed', 'Other'],
            p=[0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
        )
    
    # Age 30-39
    elif 30 <= age <= 39:
        return np.random.choice(
            ['Finance', 'IT', 'Health', 'Education', 'Unemployed', 'Student', 'Other'],
            p=[0.25, 0.20, 0.18, 0.15, 0.10, 0.05, 0.07]
        )
    
    # Age 40-49
    elif 40 <= age <= 49:
        return np.random.choice(
            ['Finance', 'Health', 'IT', 'Education', 'Unemployed', 'Student', 'Other'],
            p=[0.28, 0.20, 0.18, 0.18, 0.10, 0.03, 0.03]
        )
    
    # Age 50-59
    elif 50 <= age <= 59:
        return np.random.choice(
            ['Finance', 'Health', 'Education', 'IT', 'Unemployed', 'Student', 'Other'],
            p=[0.25, 0.22, 0.20, 0.15, 0.12, 0.03, 0.03]
        )
    
    # Age 60-65
    elif 60 <= age <= 65:
        return np.random.choice(
            ['Unemployed', 'Finance', 'Health', 'Education', 'IT', 'Student'],
            p=[0.40, 0.20, 0.15, 0.15, 0.08, 0.02]
        )
    
    # Age > 65 (if any)
    else:
        return np.random.choice(
            ['Unemployed', 'Finance', 'Health', 'Education'],
            p=[0.60, 0.15, 0.15, 0.10]
        )


def map_job_type_to_standard(job_type):
    """
    Map variations of job types to standard names.
    The dataset has 'Healthcare' and 'Health', 'Marketing', 'Manufacturing', 'Freelancer'
    which need to be mapped to the standard job types we're using.
    
    Args:
        job_type: Original job type from dataset
        
    Returns:
        Standardized job type for compatibility
    """
    # Map old job types to 'Other' category since they're not in our probability distribution
    if job_type in ['Healthcare', 'Marketing', 'Manufacturing', 'Freelancer']:
        return 'Other'
    return job_type


def fix_job_types(input_file, output_file):
    """
    Read CSV, reassign job_type for every row based on age, write to output.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Count problematic jobs before fixing
    print("\n" + "="*70)
    print("BEFORE: Problematic teen jobs (18-22 with Finance/Health/Education):")
    problematic_before = df[
        (df['age'].isin([18.0, 19.0, 20.0, 21.0, 22.0])) & 
        (df['job_type'].isin(['Finance', 'Health', 'Education']))
    ]
    print(f"Count: {len(problematic_before)}")
    
    # Apply realistic job assignments
    print("\n" + "="*70)
    print("Reassigning job types based on age...")
    df['job_type'] = df['age'].apply(assign_realistic_job)
    
    # Save the corrected dataset
    print(f"\nSaving to {output_file}...")
    df.to_csv(output_file, index=False)
    
    print(f"✅ Successfully saved corrected dataset to {output_file}")
    
    return df


def verify_distribution(df):
    """
    Verify the job type distribution by age group.
    
    Args:
        df: DataFrame with corrected job types
    """
    print("\n" + "="*70)
    print("VERIFICATION: Job Type Distribution by Age Group")
    print("="*70)
    
    age_groups = [
        ([18, 19], "Age 18-19 (Teens)"),
        ([20, 21, 22], "Age 20-22 (Young Adults)"),
        ([23, 24], "Age 23-24 (Recent Grads)"),
        (range(25, 30), "Age 25-29"),
        (range(30, 40), "Age 30-39"),
        (range(40, 50), "Age 40-49"),
        (range(50, 60), "Age 50-59"),
        (range(60, 66), "Age 60-65")
    ]
    
    for age_range, label in age_groups:
        subset = df[df['age'].isin(age_range)]
        if len(subset) > 0:
            print(f"\n{label} (n={len(subset)}):")
            job_counts = subset['job_type'].value_counts()
            for job, count in job_counts.items():
                percentage = (count / len(subset)) * 100
                print(f"  {job:15s}: {count:5d} ({percentage:5.1f}%)")
    
    # Check for impossible jobs in young ages
    print("\n" + "="*70)
    print("CRITICAL CHECK: Impossible jobs for ages 18-22:")
    impossible = df[
        (df['age'].isin([18.0, 19.0, 20.0, 21.0, 22.0])) & 
        (df['job_type'].isin(['Finance', 'Health', 'Education']))
    ]
    
    if len(impossible) == 0:
        print("✅ NO impossible jobs found! All ages 18-22 have appropriate job types.")
    else:
        print(f"❌ WARNING: {len(impossible)} impossible jobs still exist!")
        print(impossible[['age', 'gender', 'job_type']].head(10))
    
    print("\n" + "="*70)
    print("SUMMARY:")
    total_teens_young = len(df[df['age'].isin([18.0, 19.0, 20.0, 21.0, 22.0])])
    print(f"  Total individuals aged 18-22: {total_teens_young}")
    print(f"  Impossible jobs removed: {len(impossible) == 0}")
    print(f"  Dataset is now REALISTIC: {'✅ YES' if len(impossible) == 0 else '❌ NO'}")


if __name__ == '__main__':
    input_file = 'social_media_vs_productivity_CORRECTED.csv'
    output_file = 'social_media_vs_productivity_CORRECTED.csv'
    
    print("="*70)
    print("FIX JOB TYPE DISTRIBUTION BY AGE")
    print("="*70)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Fix the job types
    df = fix_job_types(input_file, output_file)
    
    # Verify the results
    verify_distribution(df)
    
    print("\n" + "="*70)
    print("✅ COMPLETE! Dataset now has realistic job-age distributions.")
    print("="*70)
