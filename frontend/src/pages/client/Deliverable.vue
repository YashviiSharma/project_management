<template>
	<div class="min-h-screen bg-gray-50">
		<NavBar :userName="userName" />

		<main class="container mx-auto px-4 py-8">
			<div class="flex justify-between items-center mb-6">
				<h1 class="text-2xl font-bold text-gray-800">My Deliverables</h1>
				<div class="flex space-x-2">
					<button 
						@click="activeTab = 'pending'"
						:class="`px-4 py-2 rounded ${activeTab === 'pending' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`"
					>
						Pending Review
					</button>
					<button 
						@click="activeTab = 'all'"
						:class="`px-4 py-2 rounded ${activeTab === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`"
					>
						All Deliverables
					</button>
				</div>
			</div>

			<div v-if="loading" class="text-center py-12">
				<div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
				<p class="mt-3 text-gray-600">Loading deliverables...</p>
			</div>

			<div v-else-if="filteredDeliverables.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
				<p class="text-gray-600">
					{{ activeTab === 'pending' ? 'No deliverables pending your review.' : 'No deliverables found.' }}
				</p>
			</div>

			<div v-else class="space-y-4">
				<div 
					v-for="deliverable in filteredDeliverables" 
					:key="deliverable.name"
					class="bg-white rounded-lg shadow p-6 hover:shadow-md transition"
				>
					<div class="flex justify-between items-start">
						<div>
							<h2 class="text-xl font-bold text-gray-800 mb-1">{{ deliverable.deliverable_name }}</h2>
							<p class="text-sm text-gray-500">Project: {{ getProjectName(deliverable.project) }}</p>
						</div>
						<span :class="`px-3 py-1 text-sm font-semibold rounded ${getStatusClass(deliverable.status)}`">
							{{ deliverable.status }}
						</span>
					</div>

					<div class="mt-4">
						<p class="text-sm text-gray-600 mb-3">{{ deliverable.description || 'No description provided.' }}</p>
						
						<div class="flex justify-between text-sm text-gray-600">
							<span>Due Date</span>
							<span :class="`${isOverdue(deliverable.due_date) ? 'text-red-600 font-medium' : ''}`">
								{{ formatDate(deliverable.due_date) }}
							</span>
						</div>
					</div>

					<div class="mt-6 flex justify-between items-center">
						<div>
							<span class="text-sm text-gray-500">Last updated: {{ formatDate(deliverable.modified) }}</span>
						</div>
						
						<div class="flex space-x-3">
							<button 
								v-if="deliverable.document"
								@click="downloadDeliverable(deliverable)"
								class="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center"
							>
								<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
								</svg>
								Download
							</button>
							
							<button 
								@click="openReviewDialog(deliverable)"
								class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium"
								v-if="deliverable.status === 'Awaiting Client Review'"
							>
								Submit Review
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Review Dialog -->
			<div v-if="showReviewDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
				<div class="bg-white rounded-lg shadow-xl w-full max-w-md">
					<div class="p-6">
						<h2 class="text-xl font-bold text-gray-800 mb-4">Submit Review for {{ currentDeliverable.deliverable_name }}</h2>
						
						<div class="mb-4">
							<label class="block text-gray-700 text-sm font-medium mb-2">Your Feedback</label>
							<textarea 
								v-model="reviewComment"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
								rows="4"
								placeholder="Type your feedback here..."
							></textarea>
						</div>
						
						<div class="mb-4">
							<label class="block text-gray-700 text-sm font-medium mb-2">Action</label>
							<select 
								v-model="reviewAction"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								<option value="Approve">Approve</option>
								<option value="Review">Request Changes</option>
								<option value="Reject">Reject</option>
							</select>
						</div>
						
						<div class="flex justify-end space-x-3">
							<button 
								@click="showReviewDialog = false"
								class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
							>
								Cancel
							</button>
							<button 
								@click="submitReview"
								class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
							>
								Submit Review
							</button>
						</div>
					</div>
				</div>
			</div>
		</main>

		<!-- Use the Footer component -->
		<FooterComponent />
	</div>
</template>

<script>
// Import SweetAlert2 from CDN
import 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
import NavBar from '@/components/NavBar.vue';
import FooterComponent from '@/components/Footer.vue';

export default {
	name: 'ClientDeliverables',
	components: {
		NavBar,
		FooterComponent
	},
	data() {
		return {
			userName: '',
			deliverables: [],
			projects: [],
			loading: true,
			activeTab: 'pending',
			showReviewDialog: false,
			currentDeliverable: null,
			reviewComment: '',
			reviewAction: 'Approve'
		}
	},
	computed: {
		filteredDeliverables() {
			if (this.activeTab === 'pending') {
				return this.deliverables.filter(d => d.status === 'Awaiting Client Review');
			}
			return this.deliverables;
		}
	},
	async mounted() {
		await this.getUserInfo();
		await this.fetchClientProjects();
		await this.fetchDeliverables();
	},
	methods: {
		formatDate(dateString) {
			if (!dateString) return 'N/A';
			const options = { year: 'numeric', month: 'short', day: 'numeric' };
			return new Date(dateString).toLocaleDateString(undefined, options);
		},
		
		isOverdue(dateString) {
			if (!dateString) return false;
			return new Date(dateString) < new Date();
		},
		
		getStatusClass(status) {
			switch(status) {
				case 'In Progress': return 'bg-blue-100 text-blue-800';
				case 'Awaiting Client Review': return 'bg-purple-100 text-purple-800';
				case 'Required Changes': return 'bg-yellow-100 text-yellow-800';
				case 'Approved': return 'bg-green-100 text-green-800';
				case 'Rejected': return 'bg-red-100 text-red-800';
				default: return 'bg-gray-100 text-gray-800';
			}
		},
		
		getProjectName(projectId) {
			const project = this.projects.find(p => p.name === projectId);
			return project ? project.project_name : projectId;
		},
		
		async getUserInfo() {
			try {
				const userResponse = await fetch('/api/method/frappe.auth.get_logged_user');
				if (!userResponse.ok) throw new Error('Failed to get user email');
				const userData = await userResponse.json();
				
				const profileResponse = await fetch(`/api/resource/User/${userData.message}`);
				if (!profileResponse.ok) throw new Error('Failed to get user profile');
				const profile = await profileResponse.json();
				
				this.userName = profile.data.full_name || userData.message;
			} catch (error) {
				console.error('Error fetching user info:', error);
			}
		},
		
		async fetchClientProjects() {
			try {
				const response = await fetch('/api/method/project_management.api.get_client_projects');
				if (!response.ok) throw new Error('Failed to fetch projects');
				const data = await response.json();
				this.projects = data.message || [];
			} catch (error) {
				console.error('Error fetching projects:', error);
			}
		},
		
		async fetchDeliverables() {
			try {
				this.loading = true;
				const projectNames = this.projects.map(p => p.name);
				
				const response = await fetch('/api/method/project_management.api.get_client_deliverables', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						projects: projectNames,
						include_all: true
					})
				});
				
				if (!response.ok) throw new Error('Failed to fetch deliverables');
				
				const data = await response.json();
				this.deliverables = data.message || [];
			} catch (error) {
				console.error('Error fetching deliverables:', error);
			} finally {
				this.loading = false;
			}
		},
		
		downloadDeliverable(deliverable) {
			if (deliverable.document) {
				window.open(deliverable.document, '_blank');
			}
		},
		
		openReviewDialog(deliverable) {
			this.currentDeliverable = deliverable;
			this.reviewComment = '';
			this.reviewAction = 'Approve';
			this.showReviewDialog = true;
		},
		async submitReview() {
	try {
		// Show loading state
		Swal.fire({
			title: 'Submitting review...',
			text: 'Please wait while we process your feedback',
			allowOutsideClick: false,
			didOpen: () => {
				Swal.showLoading();
			}
		});

		// Make the API request
		const response = await fetch('/api/method/project_management.api.submit_deliverable_review', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				deliverable: this.currentDeliverable.name,
				comment: this.reviewComment,
				action: this.reviewAction
			})
		});

		const data = await response.json();

		if (data.message?.status === "success") {
			await this.fetchDeliverables();
			this.showReviewDialog = false;

			Swal.fire({
				icon: 'success',
				title: 'Success!',
				text: data.message.message || 'Review submitted successfully',
				confirmButtonColor: '#3085d6'
			});
			return;
		}

		if (data.message?.status === "error") {
			throw new Error(data.message.message || 'Failed to submit review');
		}

		if (data.message === "success") {
			await this.fetchDeliverables();
			this.showReviewDialog = false;
			Swal.fire({
				icon: 'success',
				title: 'Success!',
				text: 'Review submitted successfully',
				confirmButtonColor: '#3085d6'
			});
			return;
		}

		if (data._server_messages) {
			let errorMessages;
			try {
				errorMessages = JSON.parse(data._server_messages);
				throw new Error(errorMessages.map(msg => {
					try {
						return JSON.parse(msg).message;
					} catch (e) {
						return msg;
					}
				}).join(', '));
			} catch (e) {
				throw new Error(data._server_messages);
			}
		}

		throw new Error('Failed to submit review: Unknown response format');

	} catch (error) {
		console.error('Error submitting review:', error);

		Swal.fire({
			icon: 'error',
			title: 'Error!',
			text: error.message || 'Unknown error occurred',
			confirmButtonColor: '#d33'
		});
	}
}
	}
}
</script>