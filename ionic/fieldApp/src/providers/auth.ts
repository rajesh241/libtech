import { Injectable } from '@angular/core';
import * as firebase from 'firebase/app';
import { AngularFireAuth } from 'angularfire2/auth';
import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

@Injectable()
export class Auth {
    users: AfoListObservable<any[]>;
    user: any;
    url = '/users/'
    panchayats: AfoListObservable<any[]>;

    constructor(private afAuth: AngularFireAuth, private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Hello Auth Provider');
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
    /*
        login(email, password) {
            return this.afAuth.auth.signInWithEmailAndPassword({
                email: email,
                password: password
            }, {
                    provider: AuthProviders.Password,
                    method: AuthMethods.Password
                }).then((response) => {
                    console.log('auth ' + 'Login Success' + JSON.stringify(response));
                    let user = {
                        email: response.auth.email,
                        picture: response.auth.photoURL
                    };
                    console.log('auth ' + JSON.stringify(user));
                    window.localStorage.setItem('user', JSON.stringify(user));
                }).catch((error) => {
                    console.log(error);
                    alert(error);
                });
        }
    */
    loginWithGoogle() {
        return this.afAuth.auth.signInWithPopup(
            new firebase.auth.GoogleAuthProvider()
        ).then((response) => {
            console.log('Login with Google Success' + JSON.stringify(response));
            this.user = {
                username: (response.user.email.slice(0, response.user.email.indexOf("@"))).replace(".", "_"),
                email: response.user.email,
                picture: response.user.photoURL,
                panchayats: ""
            };
            console.log(JSON.stringify(this.user));
            window.localStorage.setItem('user', JSON.stringify(this.user));
            this.users.update(this.user.username, this.user);
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    loginWithFacebook() {
        return this.afAuth.auth.signInWithPopup(
            new firebase.auth.FacebookAuthProvider()
        ).then((response) => {
            console.log('Login with Facebook Success' + JSON.stringify(response));
            this.user = {
                username: (response.user.email.slice(0, response.user.email.indexOf("@"))).replace(".", "_"),
                email: response.user.displayName,
                picture: response.user.photoURL,
                panchayats: ""
            };
            console.log(JSON.stringify(this.user));
            window.localStorage.setItem('user', JSON.stringify(this.user));
            this.users.update(this.user.username, this.user);
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    logout() {
        this.user = null;
        window.localStorage.removeItem('user');
        return this.afAuth.auth.signOut();
    }
    /*

loadPanchayats() {
    var panchayats = this.afoDatabase.list(this.url + this.user.username + '/panchayats/');
    panchayatsChosen.forEach(panchayat => {
        console.log('Updating for panchayat = ' + panchayat);
        panchayats.update(panchayat, {});
    });
}
    */

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
            this.panchayats = this.user.panchayats.split(", ");
            console.log(this.panchayats);
            return this.panchayats;
        }
    }


    update(panchayatsChosen) {
        this.user['panchayats'] = panchayatsChosen.join(", "); // JSON.stringify(panchayatsChosen);
        console.log(this.user);
        console.log(this.users);
        console.log(JSON.stringify(panchayatsChosen));
        window.localStorage.setItem('user', JSON.stringify(this.user));
        this.users.update(this.user.username, this.user);
    }
}
