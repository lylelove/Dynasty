<template>
   <el-table :data="event_show">
        <el-table-column prop="time" label="时间" >
        </el-table-column>
        <el-table-column prop="event" label="事件" >
        </el-table-column>
    </el-table>
</template>

<script>
export default {
    name:'Event',
    data() {
        return {
            event_show:[
            ],
            event_list:[
                {
                time:"",
                event:'今年无事发生。',
                emperor_hp_change:0,
                dynasty_hp_change:0,
                },{
                    time:"",
                    event:"事件2",
                    emperor_hp_change:0,
                    dynasty_hp_change:0,
                }
            ],
            data_emperor_hp_change:0,
            data_dynasty_hp_change:0,
            d_time:"",
            d_event:"",
            d_event_id:0,
        }
    },
    methods:{
        event_change(){
            if(this.event_list[this.d_event_id].emperor_hp_change!=null){
                this.data_emperor_hp_change = this.event_list[this.d_event_id].emperor_hp_change;
            }
            if(this.event_list[this.d_event_id].dynasty_hp_change!=null){
                this.data_dynasty_hp_change = this.event_list[this.d_event_id].dynasty_hp_change;
            }
        },
    }
}
</script>

<style>

</style>