import { Observable } from 'rxjs/Observable';
var EmulateQuery = (function () {
    function EmulateQuery() {
        this.query = {};
        this.subscriptions = [];
    }
    EmulateQuery.prototype.destroy = function () {
        this.subscriptions.forEach(function (sub) { return sub.unsubscribe(); });
        this.subscriptions = [];
    };
    /**
     * Gets the latest value of all query items, including Observable queries.
     *
     * If the query item's value is an observable, then we need to listen to that and update
     * the query when it updates.
     * @see https://goo.gl/mNVjGN
     */
    EmulateQuery.prototype.setupQuery = function (options) {
        var _this = this;
        // Store passed options
        this.observableOptions = options;
        // Ignore empty queries
        if (this.observableOptions === undefined || this.observableOptions.query === undefined) {
            return;
        }
        // Loop through query items
        this.queryReady = Promise.all(Object.keys(this.observableOptions.query).map(function (queryKey) {
            return new Promise(function (resolve) {
                // Checks if the query item is an observable
                if (_this.observableOptions.query[queryKey] instanceof Observable) {
                    _this.subscriptions.push(_this.observableOptions.query[queryKey].subscribe(function (value) {
                        _this.query[queryKey] = value;
                        resolve();
                    }));
                    // Otherwise it's a regular query (e.g. not an Observable)
                }
                else {
                    _this.query[queryKey] = _this.observableOptions.query[queryKey];
                    resolve();
                }
            });
        }));
    };
    /**
     * Emulates the query that would be applied by AngularFire2
     *
     * Using format similar to [angularfire2](https://goo.gl/0EPvHf)
     */
    EmulateQuery.prototype.emulateQuery = function (value) {
        var _this = this;
        this.observableValue = value;
        if (this.observableOptions === undefined
            || this.observableOptions.query === undefined
            || this.observableValue === undefined) {
            return new Promise(function (resolve) { return resolve(_this.observableValue); });
        }
        return this.queryReady.then(function () {
            // Check orderBy
            if (_this.query.orderByChild) {
                _this.orderBy(_this.query.orderByChild);
            }
            else if (_this.query.orderByKey) {
                _this.orderBy('$key');
            }
            else if (_this.query.orderByPriority) {
                _this.orderBy('$priority');
            }
            else if (_this.query.orderByValue) {
                _this.orderBy('$value');
            }
            // check equalTo
            if (hasKey(_this.query, 'equalTo')) {
                if (hasKey(_this.query.equalTo, 'value')) {
                    _this.equalTo(_this.query.equalTo.value, _this.query.equalTo.key);
                }
                else {
                    _this.equalTo(_this.query.equalTo);
                }
                if (hasKey(_this.query, 'startAt') || hasKey(_this.query, 'endAt')) {
                    throw new Error('Query Error: Cannot use startAt or endAt with equalTo.');
                }
                // apply limitTos
                if (!isNil(_this.query.limitToFirst)) {
                    _this.limitToFirst(_this.query.limitToFirst);
                }
                if (!isNil(_this.query.limitToLast)) {
                    _this.limitToLast(_this.query.limitToLast);
                }
                return _this.observableValue;
            }
            // check startAt
            if (hasKey(_this.query, 'startAt')) {
                if (hasKey(_this.query.startAt, 'value')) {
                    _this.startAt(_this.query.startAt.value, _this.query.startAt.key);
                }
                else {
                    _this.startAt(_this.query.startAt);
                }
            }
            if (hasKey(_this.query, 'endAt')) {
                if (hasKey(_this.query.endAt, 'value')) {
                    _this.endAt(_this.query.endAt.value, _this.query.endAt.key);
                }
                else {
                    _this.endAt(_this.query.endAt);
                }
            }
            if (!isNil(_this.query.limitToFirst) && _this.query.limitToLast) {
                throw new Error('Query Error: Cannot use limitToFirst with limitToLast.');
            }
            // apply limitTos
            if (!isNil(_this.query.limitToFirst)) {
                _this.limitToFirst(_this.query.limitToFirst);
            }
            if (!isNil(_this.query.limitToLast)) {
                _this.limitToLast(_this.query.limitToLast);
            }
            return _this.observableValue;
        });
    };
    EmulateQuery.prototype.endAt = function (value, key) {
        var orderingBy = key ? key : this.orderKey;
        this.observableValue = this.observableValue.filter(function (item) { return item[orderingBy] <= value; });
    };
    EmulateQuery.prototype.equalTo = function (value, key) {
        var orderingBy = key ? key : this.orderKey;
        this.observableValue = this.observableValue.filter(function (item) { return item[orderingBy] === value; });
    };
    EmulateQuery.prototype.limitToFirst = function (limit) {
        if (limit < this.observableValue.length) {
            this.observableValue = this.observableValue.slice(0, limit);
        }
    };
    EmulateQuery.prototype.limitToLast = function (limit) {
        if (limit < this.observableValue.length) {
            this.observableValue = this.observableValue.slice(-limit);
        }
    };
    EmulateQuery.prototype.orderBy = function (x) {
        this.orderKey = x;
        this.observableValue.sort(function (a, b) {
            var itemA = a[x];
            var itemB = b[x];
            if (itemA < itemB) {
                return -1;
            }
            if (itemA > itemB) {
                return 1;
            }
            return 0;
        });
    };
    EmulateQuery.prototype.startAt = function (value, key) {
        var orderingBy = key ? key : this.orderKey;
        this.observableValue = this.observableValue.filter(function (item) { return item[orderingBy] >= value; });
    };
    return EmulateQuery;
}());
export { EmulateQuery };
export function isNil(obj) {
    return obj === undefined || obj === null;
}
export function hasKey(obj, key) {
    return obj && obj[key] !== undefined;
}
