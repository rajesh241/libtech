import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { AngularFire, FirebaseListObservable } from 'angularfire2'

/*
  Generated class for the Panchayats provider.

  See https://angular.io/docs/ts/latest/guide/dependency-injection.html
  for more info on providers and Angular 2 DI.
*/
@Injectable()
export class Jobcards {
    items: FirebaseListObservable<any>;

    constructor(private af: AngularFire) {
        //        console.log('Hello Jobcards Provider');
        this.items = af.database.list('/jobcard/KURHANI');
    }

    // Load all github users
    load(): FirebaseListObservable<any> {
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
