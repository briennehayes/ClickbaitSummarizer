library(plyr)
library(dplyr)
library(tidyr)
library(ggplot2)
library(extrafont)

font_import(pattern="cmunss")
loadfonts(device = "win")

stats <- read.csv("Results/title_stats.csv")
stats <- stats[-c(1), ]
colnames(stats)[1] <- 'id'
colnames(stats)[2] <- 'source'
truth <- read.csv("Results/truth_values.csv")
nums <- read.csv("Results/num_stats.csv")
nums <- within(nums, startsWithNum <- factor(startsWithNum, labels = c(0, 1)))
nums <- within(nums, isListicle <- factor(isListicle, labels = c(0, 1)))

data <- merge(truth, stats, by = "id") %>%
  mutate(NonAnalytic = 100 - Analytic) %>%
  merge(nums, by = "id") %>%
  gather(key = "dim", value = "value", WC:isListicle) %>%
  mutate(value = as.numeric(value)) %>%
  filter(dim %in% c('ipron', 'ppron', 'adverb', 'article',
                    'number', 'startsWithNum', 'isListicle',
                    'you', 'interrog', 'NonAnalytic')) %>%
  mutate(dim = revalue(dim, c('ipron' = 'Indefinite Pronouns',
                              'ppron' = 'Personal Pronouns',
                              'adverb' = 'Adverbs',
                              'article' = 'Articles',
                              'number' = 'Numerals',
                              'startsWithNum' = '# Initial',
                              'isListicle' = 'Listicle',
                              'you' = '2nd Person Pronouns', 
                              'interrog' = 'Interrogatives',
                              'NonAnalytic' = 'Non-Analytic Words')))

corr <- data %>%
  group_by(dim) %>%
  summarise(
    meanCorr = cor.test(truthMean, value)$estimate,
    meanCorrP = cor.test(truthMean, value)$p.value,
    medCorr = cor.test(truthMedian, value)$estimate,
    medCorrP = cor.test(truthMedian, value)$p.value
  )

avgs <- data %>%
  group_by(truthClass, dim) %>%
  summarise(mean = mean(value)) %>%
  ungroup() %>%
  mutate(truthClass = revalue(truthClass, c('no-clickbait' = 'not clickbait')))

data1 <- avgs %>%
  filter(dim %in% c('2nd Person Pronouns', 'Adverbs', 'Articles', 'Indefinite Pronouns',
                    'Interrogatives', 'Numerals', 'Personal Pronouns'))

data2 <- avgs %>%
  filter(dim %in% c('# Initial', 'Listicle'))

data3 <- avgs %>%
  filter(dim %in% 'Non-Analytic Words')

plot1 <- ggplot(data1, aes(x = truthClass, y = mean, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_wrap(~dim) +
  labs(x = "", y = "Mean % of Words in Dictionary") +
  scale_fill_manual(values=c("#696969", "#C0C0C0")) +
  guides(fill=guide_legend(title="")) +
  theme_minimal() +
  theme(
    legend.position = c(0.85, 0.15), # c(0,0) bottom left, c(1,1) top-right.
    legend.background = element_rect(fill = "white", colour = NA, size = 2),
    legend.key.size = unit(1, "cm"),
    axis.text.x=element_blank(),
    text=element_text(size=8,  family="CMU Sans Serif")
  ) 

# ggsave("plot1.png", plot = plot1, width = 3, height = 3, units = "in")

##################################
# Poster Plots
##################################

library(showtext)

font_add_google("Lato", "lato")
showtext_auto()

cgap <- avgs %>%
  ungroup() %>%
  filter(dim %in% c('ipron', 'ppron', 'adverb', 'article')) %>%
  mutate(dim = revalue(dim, c('ipron' = 'Indefinite Pronouns',
                              'ppron' = 'Personal Pronouns',
                              'adverb' = 'Adverbs',
                              'article' = 'Articles'))) %>%
  mutate(truthClass = revalue(truthClass, c('no-clickbait' = 'not clickbait')))

g <- ggplot(cgap, aes(x = truthClass, y = mean, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_grid(.~dim) +
  labs(x = "", y = "Mean % of Headline Words in Category") +
  scale_fill_manual(values=c("#990000", "#FFCC00")) +
  guides(fill=guide_legend(title="")) +
  theme_minimal() +
  theme(text = element_text(size = 32, family = "lato"), 
        axis.text.x=element_blank())
print(g)

ggsave("cgapPlot.png", plot = g, width = 6, height = 4, units = "in")

# Plotting Sensemaking

nums <- read.csv("Results/num_stats.csv")
nums <- within(nums, startsWithNum <- factor(startsWithNum, labels = c(0, 1)))
nums <- within(nums, isListicle <- factor(isListicle, labels = c(0, 1)))

# First, we do the pop. proportion stats

num_data <- merge(truth, nums, by = "id") %>%
  gather(key = "dim", value = "value", startsWithNum:isListicle) %>%
  mutate(dim = revalue(dim, c('startsWithNum' = '# Initial',
                              'isListicle' = 'Listicle'))) %>%
  mutate(value = as.numeric(value)) %>%
  mutate(truthClass = revalue(truthClass, c('no-clickbait' = 'not clickbait'))) %>%
  group_by(truthClass, dim) %>%
  summarise(proportion = sum(value) / n())

num_corr <- merge(truth, nums, by = "id") %>%
  gather(key = "dim", value = "value", startsWithNum:isListicle) %>%
  mutate(value = as.numeric(value)) %>%
  group_by(dim) %>%
  summarise(
    meanCorr = cor(truthMean, value),
    medCorr = cor(truthMedian, value)
  )

g <- ggplot(num_data, aes(x = truthClass, y = proportion, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_grid(.~dim) +
  labs(x = "", y = "Proportion of Headlines in Category") +
  scale_fill_manual(values=c("#990000", "#FFCC00")) +
  guides(fill=FALSE) +
  theme_minimal() +
  theme(text = element_text(size = 32, family = "lato"), 
        axis.text.x=element_blank())

ggsave("listsPlot.png", plot = g, width = 4, height = 4, units = "in")

# Now mean numeral use

sense <- avgs %>%
  ungroup() %>%
  filter(dim %in% c('number')) %>%
  mutate(dim = revalue(dim, c('number' = 'Numerals'))) %>%
  mutate(truthClass = revalue(truthClass, c('no-clickbait' = 'not clickbait')))

g <- ggplot(sense, aes(x = truthClass, y = mean, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_grid(.~dim) +
  labs(x = "", y = "Mean % of Numeral Words in Headline") +
  scale_fill_manual(values=c("#990000", "#FFCC00")) +
  guides(fill=FALSE) +
  theme_minimal() +
  theme(text = element_text(size = 32, family = "lato"), 
        axis.text.x=element_blank())

ggsave("numsPlot.png", plot = g, width = 2, height = 4, units = "in")

# Plotting Engagement

engage <- avgs %>%
  ungroup() %>%
  filter(dim %in% c('you', 'interrog', 'Analytic')) %>%
  mutate(dim = revalue(dim, c('you' = '2nd Person Pronouns', 
                              'interrog' = 'Interrogatives',
                              'Analytic' = 'Analytic Words'))) %>%
  mutate(truthClass = revalue(truthClass, c('no-clickbait' = 'not clickbait')))

# Since scales are so different, split Analytic words into its own plot

eng1 <- engage %>%
  filter(dim == 'Analytic Words')

g <- ggplot(eng1, aes(x = truthClass, y = mean, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_grid(.~dim) +
  labs(x = "", y = "Mean % of Headline Words in Category") +
  scale_fill_manual(values=c("#990000", "#FFCC00")) +
  guides(fill=FALSE) +
  theme_minimal() +
  theme(text = element_text(size = 32, family = "lato"), 
        axis.text.x=element_blank())

ggsave("analyticPlot.png", plot = g, width = 1.5, height = 4, units = "in")

eng2 <- engage %>%
  filter(dim != 'Analytic Words')

g <- ggplot(eng2, aes(x = truthClass, y = mean, fill = truthClass)) +
  geom_bar(stat = "identity") +
  facet_grid(.~dim) +
  labs(x = "", y = "Mean % of Headline Words in Category") +
  scale_fill_manual(values=c("#990000", "#FFCC00")) +
  guides(fill=FALSE) +
  theme_minimal() +
  theme(text = element_text(size = 32, family = "lato"), 
        axis.text.x=element_blank())

ggsave("engagePlot.png", plot = g, width = 4.5, height = 4, units = "in")

plot_data <- data %>%
  filter(dim %in% c('ipron', 'ppron'))

