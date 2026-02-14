import os
from glob import glob
import matplotlib.pyplot as plt
from time import strftime, gmtime

import optuna
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import skew, kurtosis
from optuna.distributions import CategoricalDistribution, IntDistribution, FloatDistribution

from constants import NO_OPTIMIZE_COLUMNS, OBJECTIVE_COLUMN, FAILED_COLUMN, FAILED_SCORE


KDE_SIGMA = 0.5
MIN_SCORE = 0
MAX_SCORE = 10


def sanitize_params(params, distributions):
    for param_name, param_value in params.items():
        distribution = distributions[param_name]

        if isinstance(distribution, CategoricalDistribution):
            continue

        if param_value < distribution.low or param_value > distribution.high:
            param_value = min(max(param_value, distribution.low), distribution.high)

        param_value = round((param_value - distribution.low) / distribution.step) * distribution.step + distribution.low
        if isinstance(distribution, IntDistribution):
            param_value = int(param_value)

        params[param_name] = param_value
    return params


def get_distributions(metadata_df, unique_category_dict):
    all_parameter_rows = metadata_df['type'] == 'parameter'
    parameter_metadata_df = metadata_df[all_parameter_rows]

    distributions = {}
    for index, row in parameter_metadata_df.iterrows():
        name = row['name']
        type_ = row['parameter type']
        low = row['low']
        high = row['high']
        step = row['step']

        if type_ == 'category':
            unique_categories = unique_category_dict[name]
            distributions[name] = CategoricalDistribution(choices=unique_categories)
        elif type_ == 'int':
            distributions[name] = IntDistribution(low=low, high=high, step=step)
        elif type_ == 'float':
            distributions[name] = FloatDistribution(low=low, high=high, step=step)
    return distributions


def get_formatted_parameter(parameter, value, metadata_df, fixed=False):
    fixed_string = "[FIXED]" if fixed else "       "
    parameter_metadata_rows = metadata_df['name'] == parameter
    parameter_metadata = metadata_df[parameter_metadata_rows]
    unit = parameter_metadata['unit'].values[0]

    if unit == 'seconds':
        formatted_time = strftime("%M:%S", gmtime(value))
        value = f"{formatted_time} [{value}]"

    return f"{fixed_string} {parameter:>30}:   {value:>20}   {unit}"


def get_score_columns(metadata_df):
    all_score_rows = metadata_df['type'] == 'score'
    all_score_names = metadata_df[all_score_rows]['name']
    all_score_columns = all_score_names.values
    return all_score_columns


def get_parameter_columns(metadata_df):
    all_parameter_rows = metadata_df['type'] == 'parameter'
    all_parameter_names = metadata_df[all_parameter_rows]['name']
    all_parameter_columns = all_parameter_names.values
    return all_parameter_columns


def filter_score_columns(all_score_columns, persons):
    if persons:
        score_columns = [col for col in all_score_columns if any(name in col for name in persons)]
        persons_string = ', '.join(persons)
        print(f"Only considering results for persons: {persons_string}")
        return score_columns
    else:
        return all_score_columns


def get_data_from_path(path):
    experiments_path = f"{path}data.csv"
    metadata_path = f"{path}meta.csv"
    experiments_df = get_experiments_from_path(experiments_path)
    metadata_df = get_metadata_from_path(metadata_path)
    return experiments_df, metadata_df


def get_experiments_from_path(path):
    experiments_df = pd.read_csv(path)
    experiments_df.drop(columns=NO_OPTIMIZE_COLUMNS, inplace=True)  # drop nonessential data
    experiments_df[FAILED_COLUMN] = experiments_df[FAILED_COLUMN].notna()  # make failed true/false
    return experiments_df


def get_metadata_from_path(path):
    metadata_df = pd.read_csv(path)
    return metadata_df


def parse_experiments(experiments_df, metadata_df, persons, method):
    all_score_columns = get_score_columns(metadata_df)
    all_parameter_columns = get_parameter_columns(metadata_df)
    person_score_columns = filter_score_columns(all_score_columns, persons)

    historical_experiments_df = experiments_df.dropna(subset=all_parameter_columns)
    fixed_parameters_df = experiments_df.drop(historical_experiments_df.index)
    historical_experiments_df = historical_experiments_df.copy()

    scores = get_scores(historical_experiments_df, person_score_columns, method)
    historical_experiments_df[OBJECTIVE_COLUMN] = scores
    historical_experiments_df.drop(columns=all_score_columns, inplace=True)  # score can be missing for single persons

    failed_locations = historical_experiments_df[FAILED_COLUMN]
    historical_experiments_df.loc[failed_locations, OBJECTIVE_COLUMN] = FAILED_SCORE

    if len(fixed_parameters_df) > 1:
        print("Missing historic parameter(s)!")
        exit(1)

    fixed_parameters = {}
    if not fixed_parameters_df.empty:
        fixed_parameters_df = fixed_parameters_df.iloc[0]
        fixed_parameters_df = fixed_parameters_df.dropna()
        fixed_parameters_df = fixed_parameters_df.drop(FAILED_COLUMN)
        fixed_parameters = fixed_parameters_df.to_dict()

    unique_category_dict = get_unique_categories(historical_experiments_df, metadata_df)

    return historical_experiments_df, fixed_parameters, unique_category_dict


def get_unique_categories(historical_experiments_df, metadata_df):
    categorical_parameter_rows = (metadata_df['type'] == 'parameter') & (metadata_df['parameter type'] == 'category')
    categorical_parameter_df = metadata_df[categorical_parameter_rows]
    categorical_parameter_rows = categorical_parameter_df['name']
    categorical_parameter_names = categorical_parameter_rows.values

    unique_category_dict = {}
    for categorical_parameter_name in categorical_parameter_names:
        unique_categories = historical_experiments_df[categorical_parameter_name].unique()
        unique_category_dict[categorical_parameter_name] = unique_categories
    return unique_category_dict


def get_scores(historical_experiments_df, person_score_columns, method):
    # historical_experiments_df[person_score_columns] = historical_experiments_df[person_score_columns].notna()  # make failed true/false
    if method == 'mean':
        scores = historical_experiments_df[person_score_columns].mean(axis=1)
    elif method == 'median':
        scores = historical_experiments_df[person_score_columns].median(axis=1)
    elif method == 'lowest':
        scores = historical_experiments_df[person_score_columns].min(axis=1)
    elif method == 'highest':
        scores = historical_experiments_df[person_score_columns].max(axis=1)
    return scores


def visualize(study, experiments_df, metadata_df, args):
    do_visualization = any((args.time, args.relations, args.edf, args.importance, args.slice))
    if not study.trials or not do_visualization:
        return

    png_files = glob('visualizations/*.png')
    for file_path in png_files:
        os.remove(file_path)

    if args.time:
        optuna.visualization.matplotlib.plot_optimization_history(study)
        plt.tight_layout()
        plt.savefig('visualizations/time.png')
    if args.relations:
        importances = optuna.importance.get_param_importances(study)
        params_sorted = list(importances.keys())
        optuna.visualization.matplotlib.plot_contour(study, params=params_sorted)
        plt.savefig('visualizations/relations.png')
    if args.edf:
        optuna.visualization.matplotlib.plot_edf(study)
        plt.savefig('visualizations/EDF.png')
    if args.importance:
        optuna.visualization.matplotlib.plot_param_importances(study)
        plt.tight_layout()
        plt.savefig('visualizations/importance.png')
    if args.slice:
        optuna.visualization.matplotlib.plot_slice(study)
        plt.savefig('visualizations/slice.png')
    if args.scores:
        all_score_columns = get_score_columns(metadata_df)
        person_score_columns = filter_score_columns(all_score_columns, args.persons)
        scores_df = experiments_df[person_score_columns]
        visualize_scores(scores_df)
        plt.savefig('visualizations/scores.png')

    plt.show()


def visualize_scores(scores_df):
    plt.figure()
    sns.set(style="whitegrid")
    palette = sns.color_palette("tab10", n_colors=len(scores_df.columns))

    for idx, column in enumerate(scores_df.columns):
        cleaned_column = scores_df[column].dropna()
        color = palette[idx]

        variance = cleaned_column.var()
        if pd.isna(variance) or variance == 0:
            print(f"Skipping {column} due to zero variance.")
            continue

        sns.kdeplot(
            cleaned_column,
            label=f"{column}", fill=True, color=color, bw_adjust=KDE_SIGMA,
            )
        plt.scatter(
            cleaned_column, np.zeros_like(cleaned_column),
            color=color, s=20, zorder=3, alpha=0.1)

    y_min, y_max = plt.gca().get_ylim()  # have to get y_lims for placing text

    for idx, column in enumerate(scores_df.columns):
        cleaned_column = scores_df[column].dropna()
        color = palette[idx]

        mean = cleaned_column.mean()
        variance = cleaned_column.var()
        skewness = skew(cleaned_column, bias=False)
        kurt = kurtosis(cleaned_column, bias=False)

        # Line and text at mean
        plt.axvline(mean, color=color, linestyle='--')
        y_pos = y_max - (y_max - y_min) * (1/len(scores_df.columns)) * idx
        plt.text(
            mean + 0.1, y_pos,
            f'{column}\nMean: {mean:.2f}\nVar: {variance:.2f}\nSkew: {skewness:.2f}\nKurtosis: {kurt:.2f}',
            horizontalalignment='left', verticalalignment='top', size='small', color=color)

    plt.xlim(MIN_SCORE, MAX_SCORE)
    plt.legend()
    plt.title('Kernel Density Estimate of Scores')
    plt.xlabel('Score')
    plt.ylabel('Density')


def get_objective(distributions, fixed_parameters):

    def objective(trial):
        for param_name, distribution in distributions.items():
            if param_name in fixed_parameters:
                continue

            if isinstance(distribution, optuna.distributions.CategoricalDistribution):
                trial.suggest_categorical(
                    param_name, distribution.choices)
            elif isinstance(distribution, optuna.distributions.IntDistribution):
                trial.suggest_int(
                    param_name, distribution.low, distribution.high, step=distribution.step)
            elif isinstance(distribution, optuna.distributions.FloatDistribution):
                trial.suggest_float(
                    param_name, distribution.low, distribution.high, step=distribution.step)

        return 0  # dummy objective value

    return objective


def add_historical_trials(study, distributions, historical_experiments_df):
    for _, row in historical_experiments_df.iterrows():
        params = row.to_dict()
        failed = params.pop(FAILED_COLUMN)
        objective_value = params.pop(OBJECTIVE_COLUMN)
        params = sanitize_params(params, distributions)

        if pd.isna(objective_value):
            continue

        if failed:
            trial_state = optuna.trial.TrialState.FAIL
            objective_value = None
        else:
            trial_state = optuna.trial.TrialState.COMPLETE

        trial = optuna.trial.create_trial(
            distributions=distributions,
            params=params,
            value=objective_value,
            state=trial_state,
        )
        study.add_trial(trial)
