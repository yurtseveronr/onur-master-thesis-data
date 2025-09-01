#!/usr/bin/env python3
import boto3
from datetime import datetime
from collections import defaultdict

def get_resource_creation_times(stack_name, region='us-east-1'):
    """Get creation times for all resources in a CloudFormation stack"""
    
    cf_client = boto3.client('cloudformation', region_name=region)
    
    print(f"Analyzing stack: {stack_name}")
    print("=" * 80)
    
    try:
        # Get all stack events
        paginator = cf_client.get_paginator('describe_stack_events')
        events = []
        
        for page in paginator.paginate(StackName=stack_name):
            events.extend(page['StackEvents'])
        
        # Process events to track resource creation times
        resources = defaultdict(dict)
        
        for event in events:
            resource_id = event.get('LogicalResourceId', 'Unknown')
            resource_type = event.get('ResourceType', 'Unknown')
            status = event.get('ResourceStatus', '')
            timestamp = event.get('Timestamp')
            
            # Skip the stack itself
            if resource_type == 'AWS::CloudFormation::Stack' and resource_id == stack_name:
                continue
            
            if resource_id not in resources:
                resources[resource_id] = {'type': resource_type}
            
            if status == 'CREATE_IN_PROGRESS':
                resources[resource_id]['start_time'] = timestamp
            elif status == 'CREATE_COMPLETE':
                resources[resource_id]['end_time'] = timestamp
                resources[resource_id]['success'] = True
            elif status == 'CREATE_FAILED':
                resources[resource_id]['end_time'] = timestamp
                resources[resource_id]['success'] = False
        
        # Calculate durations and sort
        resource_durations = []
        
        for resource_id, data in resources.items():
            if 'start_time' in data and 'end_time' in data:
                duration = (data['end_time'] - data['start_time']).total_seconds()
                resource_durations.append({
                    'id': resource_id,
                    'type': data['type'],
                    'duration': duration,
                    'success': data.get('success', False)
                })
        
        # Sort by duration (longest first)
        resource_durations.sort(key=lambda x: x['duration'], reverse=True)
        
        # Print results
        for res in resource_durations:
            if res['success']:
                print(f"✅ {res['id']} ({res['type']}): {res['duration']:.2f} seconds")
            else:
                print(f"❌ {res['id']} ({res['type']}): {res['duration']:.2f} seconds - FAILED")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <stack-name> [region]")
        print("Example: python3 script.py my-network-stack us-east-1")
        sys.exit(1)
    
    stack_name = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else 'us-east-1'
    
    get_resource_creation_times(stack_name, region)