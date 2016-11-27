from english_fitness_statistics.ngram_score import ngram_score as ns

print(ns("english_fitness_statistics/english_quadgrams.txt").score("HELLOWORLD"))
