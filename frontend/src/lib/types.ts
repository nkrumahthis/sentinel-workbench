export type Alert = {
	id: string;
	title: string;
	severity: string;
	timestamp: string;
	userName: string;
	eventName: string;
	sourceIP: string;
};

export type AlertData = {
	userName: string;
	eventName: string;
	eventTime: string;
	sourceIP: string;
	userAgent: string;
};

export type Enrichments = {
	assumedRoleDetails: {
		assumedBy: string;
		assumedAt: string;
		sourceIP: string;
		roleArn: string;
	};
	recentRoleAssumptions: [
		{
			roleArn: string;
			eventTime: string;
			sourceIP: string;
			successful: string;
		}
	];
	interestingApiCalls: [
		{
			eventName: string;
			eventSource: string;
			eventTime: string;
			sourceIP: string;
		}
	];
	serviceInteractions: {
		[key: string]: number;
	};
};
