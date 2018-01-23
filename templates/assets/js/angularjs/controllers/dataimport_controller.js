angular.module('myApp')
    .controller('DataImportController', function ($scope,mappdata, $log) {
       
        $scope.selectedtags = [];
        $scope.tags = [];
        console.log("loaded");

        $scope.refresh_tags = function(tag) {
          $(".pace").hide();
          console.log(tag);
          if (tag) {
            mappdata.searchTags(tag).then(function (data) {
              $scope.tags = data.data;
            });
          }
        };

        $scope.tag_changed = function (tag, checked){
            //this page still uses old fashion form submission, so update
            //the appropriate item so data is submitted
           $scope.selectedtagnames = [];
           var taglist = [];
           angular.forEach($scope.selectedtags, function(tag) {
             //use id cause name might contain a ,
             taglist.push(tag.id);
             $scope.selectedtagnames = taglist.join();
           });
        };


        $scope.get_obj = function(id){
          $scope.id = id;
          console.log("object id is ", $scope.id);
          if ($scope.id) {
            mappdata.getTagsForObjectId($scope.id, "DataImport").then(function(data) {
              $scope.selectedtags = data.data;
              $scope.tag_changed();
            });
          }
        };
        
        $scope.keypress = function(event) {
            if (event.which === 13)
              event.preventDefault();
          };
    });
