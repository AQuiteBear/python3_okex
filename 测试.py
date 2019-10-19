from spot import spotApi

client = spotApi.Client("", "")
data = client.get_currencys()
print(data)
