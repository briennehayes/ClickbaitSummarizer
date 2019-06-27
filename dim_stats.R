library(dplyr)
library(tidyr)
library(ggplot2)

stats <- read.csv("dim_stats.csv")

clickbait <- stats %>%
  filter(truthClass == "clickbait")

not_clickbait <- stats %>%
  filter(truthClass == "no-clickbait")

metrics <- stats %>%
  group_by(truthClass) %>%
  gather(key = "stat", value = "value", polarity:modality)

ggplot(metrics, aes (x = value)) +
  geom_histogram(bins = 20) +
  facet_wrap(truthClass~stat)

avgs <- stats %>%
  group_by(truthClass) %>%
  summarise(
    pol_mean = mean(polarity),
    subj_mean = mean(subjectivity),
    mod_mean = mean(modality)
  ) %>%
  gather(key = "stat", value = "value", pol_mean:mod_mean)

ggplot(avgs, aes(x = truthClass, y = value)) +
  geom_bar(stat = "identity") +
  facet_wrap(~stat)

counts <- stats %>%
  group_by(truthClass) %>%
  summarise(
    listicle = sum(listicle) / n(),
    leadsWithQuestion = sum(leadsWithQuestion) / n(),
    hasDeterminer = sum(hasDeterminer) / n(),
    superlative = sum(superlative) / n(),
    accusatory = sum(accusatory) / n()
  ) %>%
  gather(key = "stat", value = "proportion", listicle:accusatory)

ggplot(counts, aes(x = truthClass, y = proportion)) +
  geom_bar(stat = "identity") +
  facet_wrap(~stat)

ents <- stats %>%
  group_by(truthClass) %>%
  count(numNamedEntities) %>%
  add_tally() %>%
  mutate(proportion = n / nn) %>%
  filter(numNamedEntities < 7)

ggplot(ents, aes(x = numNamedEntities, y = proportion)) +   
  geom_bar(aes(fill = truthClass), position = "dodge", stat="identity")

sums <- stats %>%
  select(truthClass, listicle, leadsWithQuestion, hasDeterminer, superlative, accusatory) %>%
  mutate(sum = rowSums(.[2:6])) %>%
  group_by(truthClass) %>%
  count(sum) %>%
  add_tally() %>%
  mutate(proportion = n / nn)

ggplot(sums, aes(x = sum, y = proportion)) +   
  geom_bar(aes(fill = truthClass), position = "dodge", stat="identity")

features <- stats %>%
  select(id, truthClass, listicle, leadsWithQuestion, hasDeterminer, superlative, accusatory) %>%
  mutate(sum = rowSums(.[3:7])) %>%
  gather(key = "feature", value = "present", listicle:accusatory)

one_feature <- features %>%
  filter(sum == 1) %>%
  filter(present == 1) %>%
  group_by(truthClass) %>%
  count(feature) %>%
  add_tally() %>%
  mutate(proportion = n / nn)

ggplot(one_feature, aes(x = feature, y = proportion)) +   
  geom_bar(aes(fill = truthClass), position = "dodge", stat="identity")

two_feature <- features %>%
  filter(sum == 2) %>%
  filter(present ==  1) %>%
  spread(feature, feature) %>%
  replace_na(list(accusatory = "", hasDeterminer = "", leadsWithQuestion = "", listicle = "", superlative = "")) %>%
  unite(col = "features", accusatory:superlative, sep = " ") %>%
  group_by(truthClass) %>%
  count(features) %>%
  add_tally() %>%
  mutate(proportion = n / nn)

ggplot(two_feature, aes(x = features, y = proportion)) +   
  geom_bar(aes(fill = truthClass), position = "dodge", stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

three_feature <- features %>%
  filter(sum == 3) %>%
  filter(present ==  1) %>%
  spread(feature, feature) %>%
  replace_na(list(accusatory = "", hasDeterminer = "", leadsWithQuestion = "", listicle = "", superlative = "")) %>%
  unite(col = "features", accusatory:superlative, sep = " ") %>%
  group_by(truthClass) %>%
  count(features) %>%
  add_tally() %>%
  mutate(proportion = n / nn)

ggplot(three_feature, aes(x = features, y = proportion)) +   
  geom_bar(aes(fill = truthClass), position = "dodge", stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

four_feature <- features %>%
  filter(sum == 4) %>%
  filter(present ==  1) %>%
  spread(feature, feature) %>%
  replace_na(list(accusatory = "", hasDeterminer = "", leadsWithQuestion = "", listicle = "", superlative = "")) %>%
  unite(col = "features", accusatory:superlative, sep = " ") %>%
  group_by(truthClass) %>%
  count(features) %>%
  add_tally() %>%
  mutate(proportion = n / nn)
