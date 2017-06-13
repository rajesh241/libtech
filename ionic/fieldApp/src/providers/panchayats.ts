import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { Panchayat } from '../models/panchayats'

@Injectable()
export class Panchayats {
    items: AfoListObservable<Panchayat[]>;
    jobcards: AfoListObservable<any[]>;

    constructor(private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Hello Panchayats Provider');
        this.items = afoDatabase.list('/panchayats');
        console.log(this.items)
    }

    load(): AfoListObservable<Panchayat[]> {
        return this.items
    }

    fetch(user): AfoListObservable<Panchayat[]> {
        return this.items
        //        return this.afoDatabase.list('/users/' + user + '/panchayats/');
    }

    sync(panchayats) {
        panchayats.forEach(panchayat => {
            console.log(JSON.stringify(panchayat));
            var url = '/jobcards/' + panchayat;
            console.log(url);
            this.jobcards = this.afoDatabase.list('/jobcards/' + panchayat);
            this.jobcards.subscribe(jobcards => {
                jobcards.forEach(element => {
                    console.log(element['$key']);
                    this.afoDatabase.list('/transactions/' + element['$key']);
                });
            });
        });
    }
}
