from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
 
# convert series to supervised learning
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg
 


def run_lstm_model(train_X, train_y, test_X, test_y, hidden_layer_number, epochs_number, batch_size_number):
	# design network
	model = Sequential()
	model.add(LSTM(hidden_layer_number, input_shape=(train_X.shape[1], train_X.shape[2])))
	model.add(Dense(1))
	model.compile(loss='mae', optimizer='adam')
	# fit network
	history = model.fit(train_X, train_y, epochs=epochs_number, batch_size=batch_size_number, validation_data=(test_X, test_y), verbose=0, shuffle=False)

	# make a prediction
	yhat = model.predict(test_X)
	test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
	# invert scaling for forecast
	inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
	inv_yhat = scaler.inverse_transform(inv_yhat)
	inv_yhat = inv_yhat[:,0]
	# invert scaling for actual
	test_y = test_y.reshape((len(test_y), 1))
	inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
	inv_y = scaler.inverse_transform(inv_y)
	inv_y = inv_y[:,0]
	# calculate RMSE
	rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
	print(', RMSE: %.3f' % rmse)

	# plot history
	#pyplot.plot(history.history['loss'], label='train')
	#pyplot.plot(history.history['val_loss'], label='test')
	#pyplot.legend()
	#pyplot.show()

def get_training_and_predict_dataset(reframed): 
	# split into train and test sets
	values = reframed.values
	n_train_hours = 365 * 24
	train = values[:n_train_hours, :]
	test = values[n_train_hours:, :]
	# split into input and outputs
	train_X, train_y = train[:, :-1], train[:, -1]
	test_X, test_y = test[:, :-1], test[:, -1]
	# reshape input to be 3D [samples, timesteps, features]
	train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
	test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
	#print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

	return [train_X, train_y, test_X, test_y]


print('\n\n Process start~ \n\n')

# load dataset
dataset = read_csv('pollution.csv', header=0, index_col=0)
values = dataset.values
# integer encode direction
encoder = LabelEncoder()
values[:,4] = encoder.fit_transform(values[:,4])
# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# frame as supervised learning
reframed = series_to_supervised(scaled, 1, 1)
# drop columns we don't want to predict
reframed.drop(reframed.columns[[9,10,11,12,13,14,15]], axis=1, inplace=True)
#print(reframed.head())

list_training_and_predict_dataset = get_training_and_predict_dataset(reframed)

train_X = list_training_and_predict_dataset[0]
train_y = list_training_and_predict_dataset[1]
test_X = list_training_and_predict_dataset[2]
test_y = list_training_and_predict_dataset[3]

list_hidden_layer_number = [150, 125, 175, 200]
list_epochs_number = [150, 125, 175, 200]
list_batch_size_number = [72, 60, 48, 84]

print('Start loop conditions...\n')
for this_list_hidden_layer_number in list_hidden_layer_number:
	for this_epochs_number in list_epochs_number:
		for this_batch_size_number in list_batch_size_number:
			print('hidden_layer_number: ' + str(this_list_hidden_layer_number) + ', epoch_number: ' + str(this_epochs_number) + ', batch_size: ' + str(this_batch_size_number), end='')
			run_lstm_model(train_X, train_y, test_X, test_y, this_list_hidden_layer_number, this_epochs_number, this_batch_size_number)

print('\n\n All done~ \n\n')