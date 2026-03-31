from langchain_community.document_loaders.sitemap import SitemapLoader

loader = SitemapLoader(web_path="https://docs.langchain.com/sitemap.xml")

docs = loader.load()
print(len(docs))
