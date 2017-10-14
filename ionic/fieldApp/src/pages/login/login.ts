import { Component } from '@angular/core';
import {
    IonicPage,
    NavController,
    NavParams,
    LoadingController,
    Loading,
    AlertController } from 'ionic-angular';

import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { AuthProvider } from '../../providers/auth/auth';
import { EmailValidator } from '../../validators/email';

@IonicPage()
@Component({
  selector: 'page-login',
  templateUrl: 'login.html',
})
export class LoginPage {
    
    loginForm:FormGroup;
    loading:Loading;
    
    constructor(public navCtrl: NavController,
		public navParams: NavParams,
		public auth:  AuthProvider,
		public formBuilder: FormBuilder,
		public alertCtrl: AlertController,
		public loadingCtrl: LoadingController) {

	this.loginForm = formBuilder.group({
	    email: ['', Validators.compose([Validators.required, EmailValidator.isValid])],
	    password: ['', Validators.compose([Validators.required, Validators.minLength(6)])]
	});

	/*
	this.loading = this.loadingCtrl.create({
	    content: "Please wait...",
	    duration: 3000,
	    dismissOnPageChange: true
	});
	this.loading.present();
	*/
    }

    login() {
	if (!this.loginForm.valid){
	    console.log(this.loginForm.value);
	}
	else {
	    this.auth.login(this.loginForm.value.email,
			    this.loginForm.value.password)
		.then( authData => {
		    this.navCtrl.setRoot('HomePage');
		    console.log(authData);
		    
		    let user = {
			email: authData.email,
			displayName: authData.displayName,
			photoURL: authData.photoURL
		    }
		    this.postLogin(user);
		}, error => {
		    this.loading.dismiss().then(() => {
			let alert = this.alertCtrl.create({
			    message: error.message,
			    buttons: [
				{
				    text: "Ok",
				    role: 'cancel'
				}
			    ]
			});
			alert.present();	
		    });
		});
	    
	    this.loading = this.loadingCtrl.create({
		content: "Logging in...",
		dismissOnPageChange: true,
	    });

	    this.loading.present();
	}
    }

    postLogin(user) {
	this.auth.postLogin(user);
    }

    createAccount() {
	this.navCtrl.push('SignupPage');
    }

    loginWithGoogle() {
        this.auth.loginWithGoogle().then( authData => {
	    this.navCtrl.setRoot('HomePage');
	    console.log(authData);
	    console.log(authData.user);
	    
	    let user = {
		email: authData.user.email,
		displayName: authData.user.displayName,
		photoURL: authData.user.photoURL
	    }
	    this.postLogin(user);
	}, error => {
	    this.loading.dismiss().then(() => {
		let alert = this.alertCtrl.create({
		    message: error.message,
		    buttons: [
			{
			    text: "Ok",
			    role: 'cancel'
			}
		    ]
		});
		alert.present();	
	    });
	});
	
	this.loading = this.loadingCtrl.create({
	    content: "Logging in...",
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }

    loginWithFacebook() {
        this.auth.loginWithFacebook().then( authData => {
	    this.navCtrl.setRoot('HomePage');
	    console.log(authData);
	    console.log(authData.user);
	    
	    let user = {
		email: authData.user.email,
		displayName: authData.user.displayName,
		photoURL: authData.user.photoURL
	    }
	    this.postLogin(user);
	}, error => {
	    this.loading.dismiss().then(() => {
		let alert = this.alertCtrl.create({
		    message: error.message,
		    buttons: [
			{
			    text: "Ok",
			    role: 'cancel'
			}
		    ]
		});
		alert.present();	
	    });
	});
	
	this.loading = this.loadingCtrl.create({
	    content: "Logging in...",
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }

    loginWithTwitter() {
        this.auth.loginWithTwitter().then( authData => {
	    this.navCtrl.setRoot('HomePage');
	    console.log(authData);
	    console.log(authData.user);
	    
	    let user = {
		email: authData.user.email,
		displayName: authData.user.displayName,
		photoURL: authData.user.photoURL
	    }
	    this.postLogin(user);
	}, error => {
	    this.loading.dismiss().then(() => {
		let alert = this.alertCtrl.create({
		    message: error.message,
		    buttons: [
			{
			    text: "Ok",
			    role: 'cancel'
			}
		    ]
		});
		alert.present();	
	    });
	});
	
	this.loading = this.loadingCtrl.create({
	    content: "Logging in...",
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }

    logout() {
	this.navCtrl.setRoot('LoginPage'); // FIXME
        return this.auth.logout();
    }

    ionViewDidLoad() {
	console.log('ionViewDidLoad LoginPage');
    }
}
