
    time.sleep(10)
    soup = BeautifulSoup(res.text, 'html.parser')
    jvscript=json.loads(soup.find('script',type="application/ld+json").string)
    variants=json.loads(soup.findAll('script',type="application/json")[1].string)['variants']
    pricesizedict=[{'size': d['title'],'price': d['price']/100 } for d in variants ]
    tmp=list(map(lambda class_obj: extract_cls_txt(class_obj),soup.find(class_='custom-fields-wrapper').find_all(class_='custom-field')))
    tmp_dict=ChainMap(*tmp)
    prod_attr={
        'brand':soup.find(class_='brand-and-type').find("span",class_="brand").text.strip(),
        'category':soup.find(class_='brand-and-type').find("span",class_="type").text.strip() if soup.find(class_='brand-and-type').find("span",class_="type") is not None else None,
        'name':soup.find(class_='product-title').text.strip(),
        'productdesc':soup.find(class_='product-description rte').find("span").text.strip() if soup.find(class_='product-description rte').find("span") is not None else soup.find(class_='product-description rte').text.strip(),
        #'price':soup.find(class_='product-price').text.strip(),
        'url' : site,
        'scrapedate' : datetime.now().strftime("%Y-%m-%d"),
        'website' : 'https://patient-choice.com'
        }
    prod_attr.update(tmp_dict)
    final = ChainMap(*[{**prod_attr, **y} for y in pricesizedict])
    return final

def scrapebkp(site):
    print(site)
    res=requests.get(site)
    time.sleep(10)
    soup = BeautifulSoup(res.text, 'html.parser')
    jvscript=json.loads(soup.find('script',type="application/ld+json").string)
    pricedict = ChainMap(*[{re.findall(r'[0-9]+',d['url'])[0]: (d['price'],d['priceCurrency'])} for d in jvscript['offers'] ])
    sizedict =  ChainMap(*list(map(lambda size: parse_size(size),soup.find(class_='product-form').find('select',class_="original-selector").findAll('option')) if len(pricedict)>1 else [{'Size':soup.find(class_='product-form').find(class_='selector-wrapper').text.replace("Size:","").strip()}] if soup.find(class_='product-form').find(class_='selector-wrapper') is not None else [{'Size': 0}] ))
    keys=[k for k in pricedict.keys()]
    pricesizedict = [{'price':pricedict[k][0], 'cur':pricedict[k][1], 'size':sizedict[k] if len(pricedict)>1 else sizedict['Size']} for k in keys]
    tmp=list(map(lambda class_obj: extract_cls_txt(class_obj),soup.find(class_='custom-fields-wrapper').find_all(class_='custom-field')))
    tmp_dict=ChainMap(*tmp)
    prod_attr={
        'brand':soup.find(class_='brand-and-type').find("span",class_="brand").text.strip(),
        'category':soup.find(class_='brand-and-type').find("span",class_="type").text.strip() if soup.find(class_='brand-and-type').find("span",class_="type") is not None else None,
        'name':soup.find(class_='product-title').text.strip(),
        'productdesc':soup.find(class_='product-description rte').find("span").text.strip() if soup.find(class_='product-description rte').find("span") is not None else soup.find(class_='product-description rte').text.strip(),
        #'price':soup.find(class_='product-price').text.strip(),
        'url' : site,
        'scrapedate' : datetime.now().strftime("%Y-%m-%d"),
        'website' : 'https://patient-choice.com'
        }
    prod_attr.update(tmp_dict)
    final = ChainMap(*[{**prod_attr, **y} for y in pricesizedict])
    return final



from multiprocessing.pool import ThreadPool
pool = ThreadPool(4)
data = pool.map(scrape, list(enumerate(product_urls)))
data_df = pd.DataFrame(filter(None, data))
data_df.to_csv("PC_"+date.today().strftime("%Y%m%d")+".csv",
                     index=False)