# Imports
import itertools
from collections import Counter
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE, RandomOverSampler, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import average_precision_score
from sklearn.metrics import confusion_matrix, f1_score, recall_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_auc_score, roc_curve, precision_score


CRAYONS = ['#4E79A7', '#F28E2C', '#E15759', '#76B7B2', '#59A14F', '#EDC949', '#AF7AA1', '#FF9DA7', '#9C755F', '#BAB0AB']


def compute_metrics(y_test: np.ndarray, y_prediction: np.ndarray) -> Tuple[float, float, float]:
    tn, fp, fn, tp = confusion_matrix(y_test, y_prediction).ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return (accuracy, sensitivity, specificity)


def create_balanced_dataset(sampler_name, X, y):
    """
    Factory methods to create SMOTE sampler and sampling the data set.
    :param sampler_name:
    :param X input
    :param y target variable ('Class')
    :return the sampled data set
    """

    # Over-sampling methods
    if sampler_name == 'RandomOverSampler':
        sampler = RandomOverSampler(random_state=42)
    if sampler_name == 'SMOTE':
        sampler = SMOTE(random_state=42, n_jobs=-1)
    elif sampler_name == 'ADASYN':
        sampler = ADASYN(random_state=42, n_jobs=-1)

    # Under-sampling methods
    elif sampler_name == 'RandomUnderSampler':
        sampler = RandomUnderSampler(random_state=42)

    X_sampled, y_sampled = sampler.fit_sample(X, y)
    print('X={}, y={}'
          .format(X.shape, sorted(Counter(y).items())))
    print('X_sampled={}, y_sampled={}'
          .format(X_sampled.shape, sorted(Counter(y_sampled).items())))
    return X_sampled, y_sampled


# This function is from the scikit-learn documentation
# http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.get_cmap('Accent')):
    """
    This method prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    :param cm confusion matrix
    :parm classes
    :param normalize
    :param title
    :param cmap color map
    :return

    """

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.3f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    # plt.xlabel('Predicted label')


def plot_confusion_matrix_with_labels(X_test, y_test, model, predicted_class_names, *, filename: str = None):
    # Compute confusion matrix
    y_pred = model.predict(X_test)
    cnf_matrix = confusion_matrix(y_test, y_pred)
    np.set_printoptions(precision=2)

    # Plot non-normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=predicted_class_names)

    if filename:
        plt.savefig(filename)
    plt.show()
    plt.close()


def plot_roc_curve(y_test, y_probs):
    """
     This method plots the roc curve.
     :param y_test ground truth
     :param y_probs computed probabilities related to the outcome variable y
     :return

    """

    # Create true and false positive rates
    false_positive_rate, true_positive_rate, threshold = roc_curve(y_test, y_probs, pos_label=4)

    # Plot ROC curve
    plt.title('Receiver Operating Characteristic')
    plt.plot(false_positive_rate, true_positive_rate)
    plt.plot([0, 1], ls="--")
    plt.plot([0, 0], [1, 0], c=".7"), plt.plot([1, 1], c=".7")
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()


def plot_roc_curves(y_test, y_probs, labels, sample_weight=None):
    """
    This method plots the roc curves.
    :param y_test ground truth
    :param y_probs computed probabilities related to the outcome variable y
    :param labels for the curves
    :param sample_weight sample weights for auc scores
    :return figure and axes

    """

    fig, ax = plt.subplots(figsize=(9, 6))

    N, M = y_probs.shape

    for i in range(M):
        fpr, tpr, _ = roc_curve(y_test, y_probs[:, i], sample_weight=sample_weight)
        auc = roc_auc_score(y_test, y_probs[:, i], sample_weight=sample_weight)
        ax.plot(fpr, tpr, label=labels.iloc[i] + ' (AUC = {:.3f})'.format(auc))

    ax.plot([0, 0], [1, 1], linestyle='--', color='black', alpha=0.6)
    ax.set_ylabel('True Positive Rate')
    ax.set_xlabel('False Positive Rate')
    ax.set_title('ROC curve', fontsize=14)
    sns.despine()
    plt.legend(fontsize=13, loc='lower right')

    return fig, ax


def plot_recall_curve(y_test, y_score):
    """
     This method plots the roc curve.
     :param y_test ground truth
     :param y_score computed probabilities related to the outcome variable y
     :return

    """

    precision, recall, _ = precision_recall_curve(y_test, y_score)

    # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
    step_kwargs = ({'step': 'post'}
                   if 'step' in signature(plt.fill_between).parameters
                   else {})
    plt.step(recall, precision, color='b', alpha=0.2,
             where='post')
    plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    average_precision = average_precision_score(y_test, y_score)
    plt.title('2-class Precision-Recall curve: AP={0:0.2f}'.format(average_precision))


def plot_coefficients(model, labels):
    """
    This method plots a model coefficients in descending order.
    :param model
    :param labels for the plots
    :return figure and axes

    """

    coef = model.coef_
    table = pd.Series(coef.ravel(), index=labels).sort_values(ascending=True, inplace=False)

    all_ = True
    if len(table) > 20:
        reference = pd.Series(np.abs(coef.ravel()), index=labels).sort_values(ascending=False, inplace=False)
        reference = reference.iloc[:20]
        table = table[reference.index]
        table = table.sort_values(ascending=True, inplace=False)
        all_ = False

    fig, ax = plt.subplots()
    table.T.plot(kind='barh', edgecolor='black', width=0.7, linewidth=.8, alpha=0.9, ax=ax)
    ax.tick_params(axis=u'y', length=0)
    if all_:
        ax.set_title('Estimated coefficients', fontsize=14)
    else:
        ax.set_title('Estimated coefficients (twenty largest in absolute value)', fontsize=14)
    sns.despine()
    return fig, ax


def plot_histograms(X):
    """
    This method plots an histogram given a dataframe X.
    :param X
    :return figure and axes

    """

    labels = list(X.columns)

    N, p = X.shape

    rows = int(np.ceil(p / 3))

    fig, axes = plt.subplots(rows, 3, figsize=(12, rows * (12 / 4)))

    for i, ax in enumerate(fig.axes):
        if i < p:
            sns.distplot(X.iloc[:, i], ax=ax, hist_kws={'alpha': 0.9, 'edgecolor': 'black'},
                         kde_kws={'color': 'black', 'alpha': 0.7})
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_title(labels[i])
            ax.set_yticks([])
            ax.set_xticks([])
        else:
            fig.delaxes(ax)

    sns.despine()
    plt.tight_layout()

    return fig, axes


def plot_conditional_distributions(X, y, labels=[None, None]):
    """
    This method plots the conditional distributions conditioned on outcome variable y.
    :param X
    :param y
    :param labels
    :return figure and axes

    """
    variables = list(X.columns)

    N, p = X.shape

    rows = int(np.ceil(p / 3))

    fig, axes = plt.subplots(rows, 3, figsize=(11, rows * (12 / 4)))

    for i, ax in enumerate(fig.axes):

        if i < p:
            sns.kdeplot(X.loc[y == 0, variables[i]], ax=ax, label=labels[0])
            ax.set_ylim(auto=True)
            sns.kdeplot(X.loc[y == 1, variables[i]], ax=ax, label=labels[1])
            ax.set_xlabel('')
            ax.set_yticks([])
            ax.set_xticks([])
            ax.set_title(variables[i])

        else:
            fig.delaxes(ax)

    sns.despine()
    fig.tight_layout()
    # plt.show()

    return fig, axes


def plot_feature_importance(model, labels, max_features=20):
    """
    This method plots the a ranking of rhe features extracted by an ensemble mode (e.g. random forest)
    :param model
    :param labels
    :param max_features maximum features to display
    :return figure and axes

    """
    feature_importance = model.feature_importances_ * 100
    feature_importance = 100 * (feature_importance / np.max(feature_importance))
    table = pd.Series(feature_importance, index=labels).sort_values(ascending=True, inplace=False)
    fig, ax = fig, ax = plt.subplots(figsize=(9, 6))
    if len(table) > max_features:
        table.iloc[-max_features:].T.plot(kind='barh', edgecolor='black', width=0.7, linewidth=.8, alpha=0.9, ax=ax)
    else:
        table.T.plot(kind='barh', edgecolor='black', width=0.7, linewidth=.8, alpha=0.9, ax=ax)
    ax.tick_params(axis=u'y', length=0)
    ax.set_title('Variable importance', fontsize=13)
    sns.despine()
    return fig, ax


def classifiers_metric_report(models, labels, X_test, y_test):
    """
    This method generates performance metric reports for models
    :param models: list of models
    :param labels labels for roc curves
    :param X_test: testing inout
    :param y_test: ground truth
    :return report

    """

    columns = ['Precision', 'Recall', 'F1-Score', 'Specificity']
    results = pd.DataFrame(0.0, columns=columns, index=labels)

    for i, model in enumerate(models):
        y_pred = model.predict(X_test)

        precision = precision_score(y_test, y_pred)
        results.iloc[i, 0] = precision

        recall = recall_score(y_test, y_pred, average='weighted')
        results.iloc[i, 1] = recall

        f1 = f1_score(y_test, y_pred, average='weighted')
        results.iloc[i, 2] = f1

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

        specificity = tn / (tn + fp)
        results.iloc[i, 3] = specificity

    return results


def classifier_metric_report(model, model_name, X_test, y_test):
    scores = np.zeros((len(y_test), 1))
    scores[:, 0] = model.decision_function(X_test)
    return classifiers_metric_report([model], [model_name], X_test, y_test)


def plot_roc_curves_with_classifiers(scores, y_test, labels):
    with sns.color_palette(CRAYONS):
        fig, ax = plot_roc_curves(y_test, scores, labels=pd.Series(labels))
        plt.show()

    return fig, ax


def plot_roc_curves_with_classifier(scores, model, model_name):
    plot_roc_curves_with_classifiers(scores, [model], [model_name])
