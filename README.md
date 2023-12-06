# capstone

[Figma Pipelines](https://www.figma.com/file/QyKBl6YhZuI0D9D86thCc3/Pipelines?type=whiteboard&node-id=0%3A1&t=KCB0szRzkneM0i9G-1)

To scrape:
`python3 scrape_apartments.py`

To prepare the data:
`python3 prepare_data.py -data_dir data2`

To copy images from the scraping results into another folder (data2 for example)\
`cp -R scraping_results/images/ data2/images`

To make the data consistent:\
`python3 make_data_consistent.py -data_dir "data2/data.csv" -images_dir "data2/images"`

The scraping is not consistent when reproducing - apartments get added and removed from the websites.

To train the model on M1 mac, run this\
`python3 train_model.py -device "mps:0" -data data_tiny -images images_tiny -model v3`

To train the model on a Linux with CUDA, run this\
`python3 train_model.py -device "cuda" -data data -images images -model v2`
