#!/usr/bin/env python

# Run rspr

import sys
import os
import argparse
import subprocess
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

def parse_args(args=None):
    Description = "Run rspr"
    Epilog = "Example usage: rspr.py INPUT_DIR_PATH"
    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("INPUT_DIR_PATH", help="Input directory path")
    parser.add_argument("-mar", "--max_approx_rspr", dest="MAX_APPROX_RSPR_DIST", type=int, default=-1, help="Maximum approximate rSPR distance")
    parser.add_argument("-mbl", "--min_branch_length", dest="MIN_BRANCH_LENGTH", type=int, default=0, help="Minimum branch length")
    parser.add_argument("-mst", "--max_support_threshold", dest="MAX_SUPPORT_THRESHOLD", type=int, default=0, help="Maximum support threshold")
    return parser.parse_args(args)

def make_heatmap(results, output_path):
    print("Generating heatmap")
    data = results.groupby(["tree_size", "exact_drSPR"]).size().reset_index(name="count")
    data_pivot = data.pivot(index="exact_drSPR", columns="tree_size", values="count").fillna(0)
    sns.heatmap(data_pivot.loc[sorted(data_pivot.index, reverse=True)], annot=True, fmt=".0f").set(
        title="Number of trees"
    )
    plt.xlabel("Tree size")
    plt.ylabel("Exact rSPR distance")
    plt.savefig(output_path)

def make_heatmap_from_csv(input_path, output_path):
    print("Generating heatmap from CSV")
    results = pd.read_csv(input_path)
    make_heatmap(results, output_path)

def make_groups(results, min_limit=10):
    print("Generating groups")
    min_group = results[results['approx_drSPR'] <= min_limit]['file_name'].tolist()
    groups = [min_group]
    
    rem_results = results[results['approx_drSPR'] > min_limit].sort_values(by='approx_drSPR', ascending=False)
    rem_length = len(rem_results)
    cur_index, grp_size, cur_appx_dist = 0, 0, -1
    while cur_index < rem_length :
        if cur_appx_dist != rem_results.iloc[cur_index]['approx_drSPR']:
            cur_appx_dist = rem_results.iloc[cur_index]['approx_drSPR']
            grp_size += 1
        cur_group_names = rem_results.iloc[cur_index:cur_index+grp_size]['file_name'].tolist()
        groups.append(cur_group_names)
        cur_index += grp_size
    return groups

def make_groups_from_csv(input_path):
    print("Generating groups from CSV")
    results = pd.read_csv(input_path)
    groups = make_groups(results, 0)
    return groups

def extract_exact_distance(text):
    for line in text.splitlines():
        if "total exact drSPR=" in line:
            distance = line.split("total exact drSPR=")[1].strip()
            return distance
    return "0"

def fpt_rspr(input_path, groups, results, min_branch_len=0, max_support_threshold=0):
    print("Calculating exact distance")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, 'rspr.exe')
    rspr_path = [exe_path, "-multifurcating", "-length " + str(min_branch_len), "-support " + str(max_support_threshold)]
    trees_path = os.path.join(input_path, "rooted_gene_trees")
    for group in groups:
        #Run this groups in parallel
        for filename in group:
            gene_tree_path = os.path.join(trees_path, filename)
            with open(gene_tree_path, 'r') as infile:
                result = subprocess.run(rspr_path, stdin=infile, capture_output=True, text=True)
                dist = extract_exact_distance(result.stdout)
                results.loc[filename, "exact_drSPR"] = dist

def main(args=None):
    args = parse_args(args)
    
    # Exact RSPR
    #'''
    phylo_dir = os.path.join(args.INPUT_DIR_PATH, "phylogenomics")
    res_path = os.path.join(phylo_dir, 'output.csv')
    results = pd.read_csv(res_path)
    if args.MAX_APPROX_RSPR_DIST >= 0:
        results = results[(results['approx_drSPR'] <= args.MAX_APPROX_RSPR_DIST)]

    groups = make_groups(results, 0)
    results.set_index('file_name', inplace=True)
    fpt_rspr(phylo_dir, groups, results, args.MIN_BRANCH_LENGTH, args.MAX_SUPPORT_THRESHOLD)

    res_path = os.path.join(phylo_dir, 'exact_output.csv')
    results.to_csv(res_path, index=True)
    fig_path = os.path.join(phylo_dir, 'exact_output.png')
    make_heatmap(results, fig_path)
    #'''

    # From CSV
    '''
    phylo_dir = os.path.join(args.INPUT_DIR_PATH, "phylogenomics")
    res_path = os.path.join(phylo_dir, 'exact_output.csv')
    fig_path = os.path.join(phylo_dir, 'exact_output.png')
    make_heatmap_from_csv(res_path, fig_path)
    '''

if __name__ == "__main__":
    sys.exit(main())