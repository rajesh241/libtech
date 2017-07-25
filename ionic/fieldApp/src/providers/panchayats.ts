import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
// import { Panchayat } from '../models/panchayats'

@Injectable()
export class Panchayats {
    items: AfoListObservable<any[]>;
    jobcards: AfoListObservable<any[]>;
    panchayats: any;
    url: string = '/panchayats/';

    constructor(private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Hello Panchayats Provider');
        this.items = afoDatabase.list(this.url, {
            query: {
                orderByChild: 'slug',
            }
        });
        console.log('PROVIDERS ');
        console.log(this.items);
        this.panchayats = [];
    }

    load() {
        console.log('Inside Load');
        if (Object.keys(this.panchayats).length != 0) // To avoid multiple subscribes
            return this.panchayats;

        this.items.subscribe(snapshots => {
            this.panchayats = {};
            snapshots.forEach(snapshot => this.panchayats[snapshot.$key] = snapshot);
	    /* Useful to populate the Firebase Database
            snapshots.forEach(panchayat => {
                let slug = panchayat.panchayatKey.replace(/_/g, ' ').replace(/-/g, '_').replace(/ /g, '-')

                this.panchayats[slug] = { 'state': panchayat.state, 'district': 'DistrictFromDjango', 'block': panchayat.block, 'name': panchayat.panchayat, 'slug': slug, 'code': 'CodeFromDjango', 'jobcardCode': panchayat.jobcardCode }
            });
	    */

            /*
            this.panchayats = snapshots;
.map(snapshot => {
            return { snapshot.$key: {
                // panchayatKey: (snapshot.state + '-' + snapshot.block + '-' + snapshot.panchayat).toLowerCase().replace(' ', '_'), 
                panchayatCode: 'fromDjango', jobcardCode: snapshot.jobcardCode, panchayatKey: snapshot.$key, panchayat: snapshot.panchayat, block: snapshot.block, state: snapshot.state
            }
        };
    }); */
            console.log('Fecthing all the panchaytas asynchronously!');
            console.log(JSON.stringify(this.panchayats));
        },
            err => { console.log('Error: ' + err) },
            () => { console.log('Load Completed!') } // Will never execute
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
