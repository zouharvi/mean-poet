# MeanPoet

A metric for evaluating poetry translation (**mean**ing & **poet**icness).
Proper description is TODO but you can look at [our poster at MTM22](meta/poster_mtm22.pdf).

## Installation

Run `pip3 install -r requirements.txt` and makes sure that:

```python3
import nltk
# tokenization, wordnet corpus, pos tagging
nltk.download("punkt", "wordnet", "omw-1.4", "averaged_perceptron_tagger")
```

You may need to install `espeak` as well (for the `Poesy` package): `sudo apt install espeak`.

## Crawled Dataset

See [src/crawl/README.md](src/crawl/README.md) for detailed description of our large crawled bilingual poetry dataset.

## Evaluated Dataset

TODO