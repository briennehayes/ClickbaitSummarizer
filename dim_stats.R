library(dplyr)

stats <- read.csv("dim_stats.csv")

clickbait <- stats %>%
  filter(truthClass == "clickbait")

not_clickbait <- stats %>%
  filter(truthClass == "no-clickbait")

avgs <- stats %>%
  group_by(truthClass) %>%
  summarise(
    pol_mean = mean(pol),
    pol_sd = sd(pol),
    subj_mean = mean(subj),
    subj_sd = sd(subj),
    mod_mean = mean(mod),
    mod_sd = sd(mod)
  )

counts <- stats %>%
  group_by(truthClass) %>%
  summarise(
    listicle = sum(listicle) / n(),
    leadsWithQuestion = sum(leadsWithQuestion) / n(),
    hasDet = sum(hasDet) / n(),
    superlative = sum(sup) / n()
  )

t.test(clickbait$pol, not_clickbait$pol, alternative = "two.sided")
t.test(clickbait$subj, not_clickbait$subj, alternative = "two.sided")
t.test(clickbait$mod, not_clickbait$mod, alternative = "two.sided")

