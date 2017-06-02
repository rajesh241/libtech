import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

@Injectable()
export class Jobcards {
    items: AfoListObservable<any>;

    constructor(private afoDatabase: AngularFireOfflineDatabase) {
        //        console.log('Hello Jobcards Provider');
        this.items = afoDatabase.list('/jobcard/KURHANI');
    }

    // Load all github users
    load(): AfoListObservable<any> {
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
