#!/bin/bash

#SBATCH --partition=p_nlp
#SBATCH --job-name=auto
#SBATCH --output=auto.out
#SBATCH --error=auto.err
#SBATCH --begin=now+3hours

# Set the source and destination directories
source_dir="/nlp/data/S2/filter_paragraph_files_v2"
destination_dir="/nlp/data/liyifei/capri-explore"

# Copy the files to the destination directory
cp -r "$source_dir" "$destination_dir"

# Change to the destination directory
cd "$destination_dir"

# Add the copied files to Git
git add filter_paragraph_files_v2

# Commit the changes
git commit -m "add filter paragraph files with valid refs"

# Push the changes to the remote repository
git push