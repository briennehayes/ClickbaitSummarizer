library(dplyr)
library(tidyr)

eval <- read.csv("Results/eval_results.csv")[,-c(1)]
colnames(eval)[1] <- "headline"
colnames(eval)[2] <- "fr"
colnames(eval)[3] <- "list"
colnames(eval)[4] <- "dr"
eval[is.na(eval)] <- 0

eval$NonAnalytic <- 100 - eval$Analytic

set.seed(101)
train_prop <- 0.9

sample <- sample.int(n = nrow(eval), size = floor(train_prop * nrow(eval)), replace = F)
train <- eval[sample, ]
test  <- eval[-sample, ]

tidy <- train %>%
  gather(key = "feature", value = "present", fr:dr) %>%
  gather(key = "measure", value = "value", WC:NonAnalytic)

results <- train %>%
  gather(key = "feature", value = "present", fr:dr) %>%
  gather(key = "measure", value = "value", WC:NonAnalytic) %>%
  filter(measure %in% c('ipron', 'ppron', 'adverb', 'article',
                        'number',
                        'you', 'interrog', 'NonAnalytic')) %>%
  group_by(measure, present) %>%
  summarise(mean = mean(value))


fr <- tidy %>%
  filter(feature == "fr") %>%
  filter(measure %in% c('ipron', 'ppron', 'adverb', 'article')) %>%
  group_by(measure, present) %>%
  summarise(mean = mean(value))

list <- tidy %>%
  filter(feature == "list") %>%
  filter(measure %in% c("number")) %>%
  group_by(measure, present) %>%
  summarise(mean = mean(value))

dr <- tidy %>%
  filter(feature == "list") %>%
  filter(measure %in% c('you', 'interrog', 'NonAnalytic')) %>%
  group_by(measure, present) %>%
  summarise(mean = mean(value))
