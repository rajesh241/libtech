import { Component } from '@angular/core';
import { IonicPage,
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
    selector: 'page-signup',
    templateUrl: 'signup.html',
})
export class SignupPage {
    
    public signupForm:FormGroup;
    public loading:Loading;
    
    constructor(public navCtrl: NavController,
		public navParams: NavParams,
		public auth: AuthProvider,
		public formBuilder: FormBuilder,
		public alertCtrl: AlertController,
		public loadingCtrl: LoadingController) {
	
	this.signupForm = formBuilder.group({
	    email: ['', Validators.compose([Validators.required, EmailValidator.isValid])],
	    password: ['', Validators.compose([Validators.minLength(6), Validators.required])]
	});
	
    }

    /**
     * If the form is valid it will call the AuthData service to sign the user up password displaying a loading
     *  component while the user waits.
     *
     * If the form is invalid it will just log the form value, feel free to handle that as you like.
     */
    signupUser(){
	if (!this.signupForm.valid){
	    console.log(this.signupForm.value);
	} else {
	    this.auth.signup(this.signupForm.value.email, this.signupForm.value.password)
		.then(() => {
		    this.navCtrl.setRoot('HomePage');
		}, (error) => {
		    this.loading.dismiss().then( () => {
			var errorMessage: string = error.message;
			let alert = this.alertCtrl.create({
			    message: errorMessage,
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
		dismissOnPageChange: true,
	    });
	    this.loading.present();
	}
    }
    
    
    ionViewDidLoad() {
	console.log('ionViewDidLoad SignupPage');
    }

}
