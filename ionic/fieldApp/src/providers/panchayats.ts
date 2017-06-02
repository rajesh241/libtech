import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { Panchayat } from '../models/panchayats'

@Injectable()
export class Panchayats {
    items: AfoListObservable<Panchayat[]>;

    constructor(private afoDatabase: AngularFireOfflineDatabase) {
        //        console.log('Hello Panchayats Provider');
        this.items = afoDatabase.list('/geo/KURHANI');
    }

    // Load all github users
    load(): AfoListObservable<Panchayat[]> {
        return this.items
        //            .map(res => <User[]>res.json());
    }

    /*
    // Get github user by providing login(username)
    loadDetails(login: string): Observable<User> {
        return this.http.get(`${this.githubApiUrl}/users/${login}`)
            .map(res => <User>(res.json()))
    }
    searchUsers(searchParam: string): Observable<User[]> {
        return af.database.list('/' + ${searchParam }`)
	//            .map(res => <User[]>(res.json().items))
    }
    */

}
