// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete.
        query: "", 
        results: [],

    };

    app.enumerate = (a) => {
        //adds an _idx field to each element of the array
        a.map((e) => {e._idx = k++;});
        return a;
    };

   
    app.search = function () {
        if (app.vue.query.length > 1)
        {
            axios.get(search_url, {params: {q:app.vue.query}}).then(
                function(result) {
                    app.vue.results = result.data.results;
                }
                
            );
        }
        else{
            app.vue.results = [];
        }
        
    }

    app.add_from_search = function (student_id) {
        console.log(student_id)
        window.location.href = '/cs-class-tracker/add_friend/' + student_id;
 
        
    }
    app.methods = {
        // Complete.
        search: app.search,
        add_from_search: app.add_from_search

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Do any initializations (e.g. networks calls) here.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);