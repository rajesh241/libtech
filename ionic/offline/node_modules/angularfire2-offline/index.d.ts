import { Optional } from '@angular/core';
import { AngularFireDatabase } from 'angularfire2/database';
import { AngularFireOfflineDatabase } from './database/database';
import { LocalUpdateService } from './database/offline-storage/local-update-service';
export { AfoListObservable } from './database/list/afo-list-observable';
export { AfoObjectObservable } from './database/object/afo-object-observable';
export { AngularFireOfflineDatabase } from './database/database';
export declare function ANGULARFIRE_OFFLINE_PROVIDER_FACTORY(parent: AngularFireOfflineDatabase, AngularFireDatabase: any, token: any, LocalUpdateService: any): AngularFireOfflineDatabase;
export declare const ANGULARFIRE_OFFLINE_PROVIDER: {
    provide: typeof AngularFireOfflineDatabase;
    deps: (typeof AngularFireDatabase | typeof LocalUpdateService | Optional[])[];
    useFactory: (parent: AngularFireOfflineDatabase, AngularFireDatabase: any, token: any, LocalUpdateService: any) => AngularFireOfflineDatabase;
};
export declare class AngularFireOfflineModule {
}
