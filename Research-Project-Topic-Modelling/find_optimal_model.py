import gensim
from gensim.models.coherencemodel import CoherenceModel
import matplotlib.pyplot as plt
import pyLDAvis.gensim_models


def measure_model(lda_model, bow_corpus, processed_corpus, dictionary):
    print('\nPerplexity: ', lda_model.log_perplexity(bow_corpus, total_docs=10000))

    # Compute Coherence Score
    coherence_model_lda = CoherenceModel(model=lda_model,
                                         texts=processed_corpus,
                                         dictionary=dictionary,
                                         coherence='c_v')

    coherence_lda = coherence_model_lda.get_coherence()
    print('\nCoherence Score: ', coherence_lda)


def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = gensim.models.ldamodel.LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary)
        model_list.append(model)
        coherence_model = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherence_model.get_coherence())

    return model_list, coherence_values


def run_optimal_model(optimal_model, bow_corpus, dictionary):
    # Select the model and print the topics
    optimal_model = optimal_model

    vis = pyLDAvis.gensim_models.prepare(optimal_model, bow_corpus, dictionary)
    pyLDAvis.save_html(vis, 'result/topics.html')


def find_optimal_model(lda_model, bow_corpus, processed_corpus, dictionary):
    # A measure of how good the model is. lower the better.
    measure_model(lda_model, bow_corpus, processed_corpus, dictionary)

    # Compute c_v coherence for various number of topics
    limit = 50
    start = 3
    step = 1
    model_list, coherence_values = compute_coherence_values(dictionary=dictionary,
                                                            corpus=bow_corpus,
                                                            texts=processed_corpus,
                                                            start=start,
                                                            limit=limit,
                                                            step=step)

    # Show graph
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend("coherence_values", loc='best')
    plt.show()  # Show the coherence scores

    # Find best model
    dict_model_cv = {model_list[i]: coherence_values[i] for i in range(len(model_list))}
    optimal_model = max(dict_model_cv, key=dict_model_cv.get)
    print(optimal_model)

    # Print the coherence scores
    for index, value in enumerate(dict_model_cv.values(), start):
        print("Num Topics =", index, " has Coherence Value of", round(value, 4))

    # Run topic modelling with the optimal model
    run_optimal_model(optimal_model, bow_corpus, dictionary)

# DONE

