import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
// import { Panchayat } from '../models/panchayats'

@Injectable()
export class Panchayats {
    items: AfoListObservable<any[]>;
    jobcards: AfoListObservable<any[]>;
    panchayats: any;
    url: string = '/ptsWithData/';

    constructor(private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Hello Panchayats Provider');
        this.items = afoDatabase.list(this.url, {
      query: {
        orderByChild: 'panchayat',
      }
    });
        console.log('PROVIDERS ' + this.items);
        this.panchayats = [];
    }

    getData(): Promise<any> {
        var promise = new Promise(resolve => {
            this.items.subscribe(
                   snapshot => {
                       resolve(snapshot);
                   })
                })

        promise.then(data => {
            console.log('DATA',data);
            this.panchayats = data;
            /*
            data.forEach(element => {
                console.log('Elements', element);
            });

            snapshots => {
                        snapshots.forEach(snapshot => {
                    })
             */
        })
        return this.panchayats;
    }
    
    load() {
        /*
        this.panchayats = this.items.map(res => res['$value']);
         */
        console.log('Inside Load');
        console.log(this.panchayats);
        this.items.subscribe(snapshots => {
            snapshots.forEach(snapshot => {
                var panchayat = snapshot['panchayat']; // FIXME .toUpperCase();
                console.log('PROVIDER_PANCHAYAT ' + panchayat);
                this.panchayats.push(panchayat);
                });
            },
            err => { console.log('Error: ' + err) },
            () => { console.log('Load Completed!') }
        );
        return this.panchayats;
    }

    sync(panchayatsChosen) {
        panchayatsChosen.forEach(panchayat => {
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
