# Poetry Data Crawl

Scripts in this directory replicate the large paralel poetry dataset based on the public metadata. 

<!-- I'm including only languages for which we have > 30 poems -->

|Dataset|Origin tag|Poem count|Languages|Scripts|
|-|-|-|-|-|
|poetrytranslation.org|`ptc`|504|{FA,AR,ES,SO,TR, ...}-EN|`ptc.py`|
|ruverses.com|`ruverses`|7622|RU-{EN,DE,ES,IT,FR,PT,NL,FI,BG,HR,HU,ET,UK, ...}|`ruverses.py`|
|TODO|TODO|TODO|TODO|TODO|
|TODO|TODO|TODO|TODO|TODO|
|TODO|TODO|TODO|TODO|TODO|
|TODO|TODO|TODO|TODO|TODO|

Run `./src/crawl/get_comparable.sh` to get all data based on the metadata file (highly recommended).
Run `./src/crawl/get_all.sh` to get all data irregardless of the metadata file.
This may result in a slightly more poems that you crawl but non-comparability with the released dataset.

In both cases, it may take a while to download.
Alternatively, [contact the authors](mailto:vilem.zouhar@gmail.com) for help or the crawled dataset (scientific non-commertial no-distribution use only) itself.
