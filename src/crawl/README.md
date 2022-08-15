# Poetry Data Crawling

Scripts in this directory replicate the large paralel poetry dataset based on the public metadata. 

|Dataset|Origin tag|Poem count|Languages|Scripts|
|-|-|-|-|-|
|poetrytranslation.org|`ptc`|TODO|TODO|`ptc.py`|
|ruverses.com|`ruverses`|TODO|TODO|`ruverses.py`|

Run `./src/crawl/get_comparable.sh` to get all data based on the metadata file.
Run `./src/crawl/get_all.sh` to get all data irregardless of the metadata file.
This may result in a slightly more poems that you crawl but non-comparability with the released dataset.

In both cases, it may take a while to download.
Alternatively, [contact the authors](mailto:vilem.zouhar@gmail.com) for the crawled dataset (scientific non-commertial no-distribution use only).
