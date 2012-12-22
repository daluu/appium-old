/**
 *	Copyright 2012 Appium Committers
 *
 *	Licensed to the Apache Software Foundation (ASF) under one
 *	or more contributor license agreements.  See the NOTICE file
 *	distributed with this work for additional information
 *	regarding copyright ownership.  The ASF licenses this file
 *	to you under the Apache License, Version 2.0 (the
 *	"License"); you may not use this file except in compliance
 *	with the License.  You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 *	Unless required by applicable law or agreed to in writing,
 *	software distributed under the License is distributed on an
 *	"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 *	KIND, either express or implied.  See the License for the
 *	specific language governing permissions and limitations
 *	under the License.
 */

#import "RCViewController.h"

@interface RCViewController ()

@end

@implementation RCViewController

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)handleTap:(UIGestureRecognizer *)gestureRecognizer {
	CGPoint locationInView = [gestureRecognizer locationInView:self.view];
	
	// Calculate the Coordinate Label Frame
	CGRect coordinateLabelFrame = CGRectMake(0, 0, 0, 0);
	coordinateLabelFrame.size.height = 20;
	coordinateLabelFrame.size.width = 100;
	// We want the label to stay 40pts from the edges
	coordinateLabelFrame.origin.x = MIN(MAX(locationInView.x - 40, 40), self.view.frame.size.width - coordinateLabelFrame.size.width - 40);
	coordinateLabelFrame.origin.y = MIN(MAX(locationInView.y - 30, 40), self.view.frame.size.height - coordinateLabelFrame.size.height - 40);
	
	// Set the frame and test of the label
	self.coordinateLabel.frame = coordinateLabelFrame;
	self.coordinateLabel.text = [NSString stringWithFormat:@"(%d, %d)", (int)locationInView.x, (int)locationInView.y];
	self.coordinateLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:18.0f];
}
@end
