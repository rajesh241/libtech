import { Injectable } from '@angular/core';

import * as firebase from 'firebase/app';
import { AngularFireAuth } from 'angularfire2/auth';
import { AngularFireOfflineDatabase, AfoListObservable, AfoObjectObservable } from 'angularfire2-offline/database';

@Injectable()
export class AuthProvider {
    
    users: AfoListObservable<any[]>;
    user: any;
    url = '/users/'
    // panchayats: AfoListObservable<any[]>;
    panchayats: any;
    panchayatObject: AfoObjectObservable<any>;
    userObject: AfoObjectObservable<any>;

    constructor(private afAuth: AngularFireAuth, private afoDatabase: AngularFireOfflineDatabase) {
	console.log('Hello AuthProvider Provider');
        this.users = afoDatabase.list(this.url);
        console.log(this.users);
    }

    isLoggedIn() {
        if (window.localStorage.getItem('user')) {
            if (!this.user) {
                this.user = JSON.parse(window.localStorage.getItem('user'));
                console.log(JSON.stringify(this.user));
            }
            return true;
        }
    }

    getUser() {
        if (window.localStorage.getItem('user')) {
            if (!this.user) {
                this.user = JSON.parse(window.localStorage.getItem('user'));
                console.log("Fetched User [" + JSON.stringify(this.user) + "]");
            }
        }
        return this.user;
    }
    
    login(email: string, password: string): firebase.Promise<any> {
	/* Mynk FIXME
	let authData = this.afAuth.auth.signInWithEmailAndPassword(email, password);
	console.log(authData);
	let user = {
	    email: authData.email,
	    name: authData.displayName,
	    picture: authData.photoURL
	}
	this.postLogin(user);
	return authData;
	*/
	return this.afAuth.auth.signInWithEmailAndPassword(email, password);
    }

    postLogin(user) {
	console.log(user);
        this.user = {
	    name: user.displayName,
            username: (user.email.slice(0, user.email.indexOf("@"))).replace(".", "_"),
            email: user.email,
            picture: user.photoURL,
            panchayats: {}
        };
	console.log(this.user);
        this.userObject = this.afoDatabase.object(this.url + this.user.username);
        console.log(this.userObject);
        this.userObject.subscribe(user => {
            console.log('User Object ' + JSON.stringify(user['$key']) + JSON.stringify(user.panchayats));
            if (!user.panchayats) {
                console.log('Update Maadi!');
            }
            else {
                console.log('Prefill Panchayats' + user.panchayats);
                this.user.panchayats = user.panchayats;
            }
        });
        this.users.update(this.user.username, this.user); // FIXME why needed when up to date?
        console.log('POST Login ' + JSON.stringify(this.user));
        window.localStorage.setItem('user', JSON.stringify(this.user));
    }
    
    resetPassword(email: string): firebase.Promise<any> {
	return this.afAuth.auth.sendPasswordResetEmail(email);
    }

    logout(): firebase.Promise<any> {
        this.user = null;
        window.localStorage.removeItem('user');
	return this.afAuth.auth.signOut();
    }

    signup(email: string, password: string): firebase.Promise<any> {
	return this.afAuth.auth.createUserWithEmailAndPassword(email, password);
    }

    loginWithGoogle() {
        return this.afAuth.auth.signInWithPopup(
            new firebase.auth.GoogleAuthProvider()
        );
    }

    loginWithFacebook() {
        return this.afAuth.auth.signInWithPopup(
            new firebase.auth.FacebookAuthProvider()
        );
    }

    loginWithTwitter() {
        return this.afAuth.auth.signInWithPopup(
            new firebase.auth.TwitterAuthProvider()
        );
    }

    userExists() {
        this.userObject = this.afoDatabase.object(this.url + this.user.username);
        //         this.userObject = this.afoDatabase.object('/users/mynk');
        // console.log(JSON.stringify(this.userObject));
        console.log(this.userObject);
        this.userObject.subscribe(user => {
            console.log('User Object ' + JSON.stringify(user['$key']) + JSON.stringify(user.panchayats));
            if (!user)
                console.log('Yippie!');
            if (!user.panchayats)
                console.log('Dippie!');
        });
        /*
        this.panchayatList = this.afoDatabase.list(this.url + this.user.username + '/panchayats/');
        // console.log(JSON.stringify(this.panchayatList));
        console.log(this.panchayatList);
        this.panchayatList.subscribe(element => {
            console.log('List ' + JSON.stringify(element));
        });
        */
        this.panchayatObject = this.afoDatabase.object(this.url + this.user.username + '/panchayats/');
        // console.log(JSON.stringify(this.panchayatObject));
        console.log(this.panchayatObject);
        this.panchayatObject.subscribe(element => {
            console.log('Panchayat Object ' + JSON.stringify(element['$key']) + element['$value']);
        });
        return this.panchayatObject;
        /*      
        var res;
        const promise = this.afoDatabase.object(this.url + this.user.username + '/panchayats/');
        promise 
            .then(_ => console.log('success'))
            .catch(err => console.log(err, 'You do not have access!'));
        */
    }

    fetch() {
        console.log('Inside Fetch');
	/*
        this.panchayats = this.afoDatabase.list('/users/' + this.user.username + '/panchayats/');
        this.panchayats.subscribe(snapshots => {
            console.log(JSON.stringify(snapshots));
            snapshots.forEach(snapshot => {
                console.log(snapshot['$key']);
                //                console.log(JSON.stringify(snapshot));
            });
        })

        return this.panchayats;
	*/
        this.user = this.getUser();
        console.log(JSON.stringify(this.user));

        if (this.user && this.user.panchayats) {
            this.panchayats = this.user.panchayats; // .split(', ');
            console.log(JSON.stringify(this.panchayats));
            return this.panchayats;
        }
    }

    update(panchayatsChosen) {
        console.log('UPDATING PanchayatList ' + JSON.stringify(panchayatsChosen));
        console.log(panchayatsChosen);
        this.user['panchayats'] = panchayatsChosen; // .join(', '); // JSON.stringify(panchayatsChosen);
        console.log(this.user);
        console.log(this.users);
        window.localStorage.setItem('user', JSON.stringify(this.user));
        this.users.update(this.user.username, this.user);
    }
    
}
