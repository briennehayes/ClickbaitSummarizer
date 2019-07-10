library(dplyr)
library(tidyr)
library(ggplot2)

vad <- read.csv("Results/vad_measures.csv")
truth <- read.csv("Results/truth_values.csv")

data <- merge(truth, vad, by = "id") %>%
  group_by(truthClass) %>%
  gather(key = "dim", value = "value", valence:dominance)

ggplot(data, aes (x = value)) +
  geom_histogram(bins = 20) +
  facet_wrap(truthClass~dim)

avgs <- data %>%
  group_by(truthClass) %>%
  spread(dim, value) %>%
  summarise(
    val_mean = mean(valence, na.rm = TRUE),
    arous_mean = mean(arousal, na.rm = TRUE),
    dom_mean = mean(dominance, na.rm = TRUE)
  ) %>%
  gather(key = "dim", value = "value", val_mean:dom_mean)
