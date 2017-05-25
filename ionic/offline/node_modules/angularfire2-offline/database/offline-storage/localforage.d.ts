import { OpaqueToken } from '@angular/core';
export declare function LocalForageToken(): OpaqueToken;
export declare function localforageFactory(): any;
export declare const LOCALFORAGE_PROVIDER: {
    provide: () => OpaqueToken;
    useFactory: () => any;
};
