import { Injectable } from '@angular/core';
import * as firebase from 'firebase/app';
import { AngularFireAuth } from 'angularfire2/auth';
import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

@Injectable()
export class Auth {
    users: AfoListObservable<any[]>;
    user: any;
    url = '/users/'

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
                let user = {
                    username: (response.user.email.slice(0, response.user.email.indexOf("@"))).replace(".", "_"),
                    email: response.user.email,
                    picture: response.user.photoURL
                };
                console.log(JSON.stringify(user));
                window.localStorage.setItem('user', JSON.stringify(user));
                this.users.update(user.username, user);
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
            let user = { 
                username: (response.user.email.slice(0, response.user.email.indexOf("@"))).replace(".", "_"),
                email: response.user.displayName,
                picture: response.user.photoURL
            };
            console.log(JSON.stringify(user));
            window.localStorage.setItem('user', JSON.stringify(user));
            this.users.update(user.username, user);
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
}
