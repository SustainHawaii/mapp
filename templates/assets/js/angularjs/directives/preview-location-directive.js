angular
.module('previewLocation', [])
.directive('previewLocation', ['$http', function($http) {
  return { 
    //bindToController: true,
    //controller: Controller,
    //controllerAs: 'vm',
    //link: link,
    restrict: 'EA',
    templateUrl: '/maps-admin/resources/partials/loc_infographic',
    scope: {
        locid: '@',
    },
    link: function ($scope, element, attrs, ctrl) {
      console.log("preview location directive link");

      $scope.$watch(function() {
        return $scope.locid; 
      }, function() {
        getLocation();
      });


      function getLocation(){
        console.log("lets get a location");
        if (($scope.locid && !($scope.location)) ||
          ($scope.location && ($scope.locid != $scope.location.id))) {
            console.log("get location in preview-location-dir");
          $http.get('/api/v1/location/' + $scope.locid + "/")
            .success(function(data){
              $scope.location = data;
              $scope.location.tags = angular.fromJson(data.tags);
              $scope.location.org = angular.fromJson(data.org);
            })
          .error(function(){});
        }
      }
    }
  };
}]);
