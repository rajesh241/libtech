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
        console.log('PROVIDERS ');
        console.log(this.items);
        this.panchayats = [];
    }

    /*
        getData(): Promise<any> {
            var promise = new Promise(resolve => {
                this.items.subscribe(
                    snapshot => {
                        resolve(snapshot);
                    })
            })
    
            promise.then(data => {
                console.log('DATA', data);
                this.panchayats = data;
                /*
                data.forEach(element => {
                    console.log('Elements', element);
                });
    
                snapshots => {
                            snapshots.forEach(snapshot => {
                        })
    
            })
            return this.panchayats;
        }
    
            console.log(this.panchayats);
            //        this.items.map(snapshots => { this.panchayats = snapshots; }); //.map(snapshot => snapshot.panchayat) }); //.map(res => <User[]>(res.json().items) { console.log(snapshots); return snapshots; });
            this.panchayats = this.items.forEach(snapshots => {
                snapshots.map(snapshot => { console.log('In Load '); console.log(snapshot); return snapshot.panchayat });
            });
            console.log('After Projection:');
            console.log(this.panchayats);
            this.items.subscribe(snapshots => {
                snapshots.map(snapshot => { console.log('In Load '); console.log(snapshot); this.panchayats.push(snapshot.panchayat); return snapshot.panchayat });
            },
                err => { console.log('Error: ' + err) },
                () => { console.log('Load Completed!') }
            );
    	
            this.panchayats = [];
            this.items.subscribe(snapshots => {
                snapshots.forEach(snapshot => this.panchayats.push(snapshot.panchayat));
            },
                err => { console.log('Error: ' + err) },
                () => { console.log('Load Completed!') }
            );
    
    */

    load() {
        console.log('Inside Load');
        if (this.panchayats.length != 0) // To avoid multiple subscribes
            return this.panchayats;

        this.items.subscribe(snapshots => {
            this.panchayats = snapshots.map(snapshot => snapshot.panchayat);
            console.log('Fecthing all the panchaytas asynchronously!');
            console.log(this.panchayats);
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
