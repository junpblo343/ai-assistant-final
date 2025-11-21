import app
x=app.GROQ_API_KEY 
print(x)
#import crypto_monitor
#X=crypto_monitor.CRYPTO_TARGETS
#print(X)
from crypto_monitor import check_prices
check_prices()
#x=crypto_monitor.get_price("bitcoin")
#print(x)
